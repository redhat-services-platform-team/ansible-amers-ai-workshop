#!/usr/bin/env ruby
# Build only public documentation. Never copy the repository or instructor files.
require 'fileutils'
require 'erb'
require 'cgi'
gem 'asciidoctor', '2.0.23'
require 'asciidoctor'

DOCS = File.expand_path(__dir__)
OUTPUT = File.expand_path('../www', DOCS)
REPOSITORY = 'https://github.com/redhat-services-platform-team/ansible-amers-ai-workshop'

def escape(value)
  CGI.escapeHTML(value.to_s)
end

def link(page)
  %(<a href="#{page[:url]}">#{page[:title]}</a>)
end

logger = Asciidoctor::MemoryLogger.new
Asciidoctor::LoggerManager.logger = logger
files = [File.join(DOCS, 'index.adoc')] + Dir[File.join(DOCS, '[0-9]*.adoc')].sort
pages = files.map do |file|
  document = Asciidoctor.load_file(file, safe: :safe, base_dir: DOCS, attributes: {
    'workshop_repo_url' => REPOSITORY, 'imagesdir' => 'assets',
    'sectanchors' => '', 'source-highlighter' => 'highlightjs'
  })
  { url: File.basename(file, '.adoc') + '.html', title: document.doctitle,
    document: document, body: document.convert }
end
abort logger.messages.map { |m| m[:message].to_s }.join("\n") unless logger.messages.empty?
site_title = pages.first[:title]
template = ERB.new(File.read(File.join(DOCS, 'layout.erb')), trim_mode: '-')
FileUtils.rm_rf(OUTPUT)
FileUtils.mkdir_p(OUTPUT)
FileUtils.cp_r(File.join(DOCS, 'assets'), OUTPUT)
File.write(File.join(OUTPUT, '.nojekyll'), '')
pages.each_with_index do |page, index|
  previous_page = index.positive? ? pages[index - 1] : nil
  next_page = pages[index + 1]
  File.write(File.join(OUTPUT, page[:url]), template.result(binding))
  # Keep bookmarks to the former Antora URLs, including section fragments.
  ['modules', 'modules/master'].each do |prefix|
    directory = File.join(OUTPUT, prefix)
    FileUtils.mkdir_p(directory)
    target = ('../' * prefix.split('/').length) + page[:url]
    File.write(File.join(directory, page[:url]), <<~HTML)
      <!doctype html><html lang="en"><head><meta charset="utf-8">
      <title>Page moved</title><meta name="robots" content="noindex">
      <meta http-equiv="refresh" content="0;url=#{target}">
      <script>location.replace(#{target.inspect} + location.search + location.hash)</script>
      </head><body><a href="#{target}">Continue to #{page[:title]}</a></body></html>
    HTML
  end
end
puts "Built #{pages.length} pages in #{OUTPUT}"
