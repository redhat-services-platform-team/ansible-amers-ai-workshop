#!/usr/bin/python
"""Run the password-free setup script and wait for its actual exit status."""
import json
import time
from ansible.module_utils.basic import AnsibleModule


def run_command(client, instance_id, script, timeout):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        info = client.describe_instance_information(Filters=[{'Key': 'InstanceIds', 'Values': [instance_id]}])
        if any(i['PingStatus'] == 'Online' for i in info['InstanceInformationList']):
            break
        time.sleep(10)
    else:
        raise RuntimeError('The instance did not register with Systems Manager before the timeout.')
    command_id = client.send_command(InstanceIds=[instance_id], DocumentName='AWS-RunShellScript',
                                     Parameters={'commands': [script], 'executionTimeout': [str(timeout)]},
                                     TimeoutSeconds=timeout)['Command']['CommandId']
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            result = client.get_command_invocation(CommandId=command_id, InstanceId=instance_id)
        except client.exceptions.InvocationDoesNotExist:
            time.sleep(5)
            continue
        status = result['Status']
        if status == 'Success':
            # The last line is the setup result. No passwords are returned from the server.
            return json.loads(result['StandardOutputContent'].strip().splitlines()[-1])
        if status in {'Failed', 'Cancelled', 'TimedOut'}:
            raise RuntimeError('Git server setup failed. Check SSM command ' + command_id + ' for diagnostic output.')
        time.sleep(5)
    client.cancel_command(CommandId=command_id, InstanceIds=[instance_id])
    raise RuntimeError('Git server setup timed out. SSM command: ' + command_id)


def main():
    module = AnsibleModule(argument_spec={
        'access_key': {'type': 'str', 'required': True, 'no_log': True},
        'secret_key': {'type': 'str', 'required': True, 'no_log': True},
        'session_token': {'type': 'str', 'default': '', 'no_log': True},
        'region': {'type': 'str', 'required': True},
        'instance_id': {'type': 'str', 'required': True},
        'script': {'type': 'str', 'required': True},
        'timeout': {'type': 'int', 'default': 1200},
    }, supports_check_mode=True)
    if module.check_mode:
        module.exit_json(changed=False, skipped=True)
    try:
        import boto3
        p = module.params
        client = boto3.Session(aws_access_key_id=p['access_key'], aws_secret_access_key=p['secret_key'],
                               aws_session_token=p['session_token'] or None, region_name=p['region']).client('ssm')
        result = run_command(client, p['instance_id'], p['script'], p['timeout'])
        module.exit_json(**result)
    except Exception as exc:
        module.fail_json(msg=str(exc))


if __name__ == '__main__':
    main()
