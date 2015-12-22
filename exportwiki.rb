class ExportWiki

  def self.export_text(p)
    c = p.content_for_version(nil)
    "#{c.text}"
  end

  # extract first version author and date 
  def self.export_extra_info(dir, p)
    File.open(dir + "/" + p.title + ".extra-info", "w") do |f|
      f.printf("'%s' '%s'\n", User.find_by_id(p.content.versions[0].author_id).login, p.content.versions[0].updated_on)
    end
  end

  def self.export_attach(dir, wikipage)
    unless wikipage.attachments.empty?
      dir = dir + "/" +  wikipage.title
      Dir.mkdir(dir)
      wikipage.attachments.each { |a|FileUtils.cp(a.diskfile,  dir + "/" + a.filename ) }
    end
    true
  end

  def self.export_wiki(dir, wiki)
    dir = dir + "/" + wiki.project.identifier
    Dir.mkdir(dir)
    wiki.pages.each do |p|
      export_attach( dir, p )
      export_extra_info( dir, p )
      File.open(dir + "/" + p.title + ".textile", "w") { |f| f.write(export_text(p)) }
    end
    true
  end


  def self.export_all
    system ("mkdir -p /tmp/redmine")
    Project.all.each { |prj| export_wiki("/tmp/redmine/", prj.wiki) }
  end

end

# vim:et:sw=2:ts=2:

