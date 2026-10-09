#!/usr/bin/python
"""Read the account's DNS zones, AMI, and existing workshop instance."""
import ipaddress
from ansible.module_utils.basic import AnsibleModule


def select_public_zone(zones, zone_id='', zone_name=''):
    public = [zone for zone in zones if not zone.get('Config', {}).get('PrivateZone', False)]
    if zone_id:
        public = [zone for zone in public if zone['Id'].split('/')[-1] == zone_id.split('/')[-1]]
    if zone_name:
        public = [zone for zone in public if zone['Name'].rstrip('.').lower() == zone_name.rstrip('.').lower()]
    if len(public) != 1:
        raise ValueError('Select exactly one public hosted zone. Set hosted_zone_id or hosted_zone_name when discovery is ambiguous.')
    return public[0]


def verify_dns_ownership(records, fqdn, owner):
    hostname = fqdn.rstrip('.').lower() + '.'
    marker = '_workshop-owner.' + hostname
    matching = [r for r in records if r['Name'].lower() == hostname]
    owners = [r for r in records if r['Name'].lower() == marker and r['Type'] == 'TXT']
    owned = any(v['Value'] == json_quote(owner) for r in owners for v in r.get('ResourceRecords', []))
    if (matching or owners) and not owned:
        raise ValueError('The Git hostname already has DNS records without this deployment owner. Choose another dns_label.')
    if any(r['Type'] not in {'A'} for r in matching):
        raise ValueError('The Git hostname has incompatible DNS records. Choose another dns_label.')


def json_quote(value):
    import json
    return json.dumps(value)


def validate_networks(vpc_cidr, subnet_cidr):
    vpc = ipaddress.ip_network(vpc_cidr)
    subnet = ipaddress.ip_network(subnet_cidr)
    if vpc.version != 4 or subnet.version != 4 or not (16 <= vpc.prefixlen <= subnet.prefixlen <= 28):
        raise ValueError('Use IPv4 VPC and subnet CIDRs with prefix lengths from 16 to 28.')
    if not subnet.subnet_of(vpc):
        raise ValueError('The subnet CIDR must be inside the VPC CIDR.')


def credential_student_ids(client, prefix, students):
    requested = {student.lower() for student in students}
    return [parameter['Name'].rsplit('/', 1)[-1]
            for page in client.get_paginator('get_parameters_by_path').paginate(
                Path=prefix, Recursive=False, WithDecryption=False)
            for parameter in page['Parameters']
            if parameter['Name'].rsplit('/', 1)[-1].lower() in requested]


def main():
    module = AnsibleModule(argument_spec={
        'access_key': {'type': 'str', 'required': True, 'no_log': True},
        'secret_key': {'type': 'str', 'required': True, 'no_log': True},
        'session_token': {'type': 'str', 'default': '', 'no_log': True},
        'region': {'type': 'str', 'required': True},
        'hosted_zone_id': {'type': 'str', 'default': ''},
        'hosted_zone_name': {'type': 'str', 'default': ''},
        'resource_name': {'type': 'str', 'required': True},
        'dns_label': {'type': 'str', 'default': 'git'},
        'environment_name': {'type': 'str', 'required': True},
        'deployment_id': {'type': 'str', 'required': True},
        'students': {'type': 'list', 'elements': 'str', 'default': []},
        'vpc_cidr': {'type': 'str', 'required': True},
        'subnet_cidr': {'type': 'str', 'required': True},
    }, supports_check_mode=True)
    try:
        import boto3
        p = module.params
        validate_networks(p['vpc_cidr'], p['subnet_cidr'])
        session = boto3.Session(aws_access_key_id=p['access_key'], aws_secret_access_key=p['secret_key'],
                                aws_session_token=p['session_token'] or None, region_name=p['region'])
        identity = session.client('sts').get_caller_identity()
        zones = [zone for page in session.client('route53').get_paginator('list_hosted_zones').paginate()
                 for zone in page['HostedZones']]
        zone = select_public_zone(zones, p['hosted_zone_id'], p['hosted_zone_name'])
        records = [record for page in session.client('route53').get_paginator('list_resource_record_sets').paginate(HostedZoneId=zone['Id'])
                   for record in page['ResourceRecordSets']]
        verify_dns_ownership(records, p['dns_label'] + '.' + zone['Name'].rstrip('.'),
                             p['deployment_id'] + '/' + p['environment_name'])
        ami = session.client('ssm').get_parameter(
            Name='/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64')['Parameter']['Value']
        reservations = session.client('ec2').describe_instances(Filters=[
            {'Name': 'tag:Name', 'Values': [p['resource_name']]},
            {'Name': 'tag:WorkshopDeployment', 'Values': [p['deployment_id']]},
            {'Name': 'instance-state-name', 'Values': ['pending', 'running', 'stopping', 'stopped']},
        ])['Reservations']
        instances = [instance for reservation in reservations for instance in reservation['Instances']]
        if len(instances) > 1:
            raise ValueError('Multiple instances match this deployment. Resolve the duplicate tags before running again.')
        known_students = credential_student_ids(session.client('ssm'),
            '/' + p['deployment_id'] + '/' + p['environment_name'] + '/students', p['students'])
        module.exit_json(changed=False, credential_student_ids=known_students, account_id=identity['Account'], partition=identity['Arn'].split(':')[1],
                         zone_id=zone['Id'].split('/')[-1], zone_name=zone['Name'].rstrip('.'),
                         ami_id=ami, instance_ids=[instance['InstanceId'] for instance in instances])
    except Exception as exc:
        module.fail_json(msg=str(exc))


if __name__ == '__main__':
    main()
