#!/usr/bin/make -f
VERSION:=0.0.22
DEBVERSION:=1
ifndef DIST
	DIST=jammy
endif
ifndef CHANGELOG
	CHANGELOG="New upstream version"
endif

clean:
	rm -Rf build debian/owebui-tmp

open-webui-tools-$(VERSION):
	mkdir open-webui-tools-$(VERSION)
	cp -a open_webui.* open-webui-tools-$(VERSION)/
	cp -a open-webui-*.conf open-webui-tools-$(VERSION)/
	cp -a owebui*.py open-webui-tools-$(VERSION)/
	cp -a Caddyfile open-webui-tools-$(VERSION)/
	cp -rfa owebui_tools open-webui-tools-$(VERSION)/
	cp -rfa pip open-webui-tools-$(VERSION)/
	cp -a pyproject.toml open-webui-tools-$(VERSION)/
	cp -a README.md open-webui-tools-$(VERSION)/
	cp -a CHANGELOG.md open-webui-tools-$(VERSION)/

open-webui-tools_$(VERSION).orig.tar.gz: open-webui-tools-$(VERSION)
	debchange --newversion $(VERSION)-$(DEBVERSION) "$(CHANGELOG)"
	tar cvzf open-webui-tools_$(VERSION).orig.tar.gz open-webui-tools-$(VERSION)/

open-webui-tools-$(VERSION)/debian: open-webui-tools-$(VERSION)
	-dpkg-buildpackage --pre-clean
	cp -Rf debian open-webui-tools-$(VERSION)/
	cp -a README.md open-webui-tools-$(VERSION)/debian/
	cp -a CHANGELOG.md open-webui-tools-$(VERSION)/

open-webui-tools_$(VERSION)-$(DEBVERSION)_source.changes: clean open-webui-tools-$(VERSION)/debian
	cd open-webui-tools-$(VERSION) && dch -l "~${DIST}" --distribution "${DIST}" "Build for PPA"
	cd open-webui-tools-$(VERSION) && dpkg-buildpackage -S
	lintian open-webui-tools_$(VERSION)-$(DEBVERSION)~${DIST}1_source.changes
	dput myppa:open-webui-tools open-webui-tools_$(VERSION)-$(DEBVERSION)~${DIST}1_source.changes

ppa:
	rm -rf open-webui-tools-$(VERSION)
	$(MAKE) open-webui-tools_$(VERSION).orig.tar.gz
	$(MAKE) DIST=noble open-webui-tools_$(VERSION)-$(DEBVERSION)_source.changes

purge:
	-mv *.dsc *.debian.tar.xz *.buildinfo *.changes *.deb *.upload *.orig.tar.gz  olds/
	rm -f ../open-webui-tools_*
	rm -f ../open-webui*.deb
	-dpkg-buildpackage --pre-clean
