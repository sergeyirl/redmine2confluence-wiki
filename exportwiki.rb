class ExportWiki

def self.export_text(p)
   c = p.content_for_version(nil)
   "#{c.text}"
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
		File.open(dir + "/" + p.title + ".textile", "w") { |f| f.write(export_text(p)) } 
		end
	true
end


def self.export_all
	Project.all.each { |prj| export_wiki("/tmp/redmine/", prj.wiki) }
end

end