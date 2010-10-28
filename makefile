#
# @author Jean-Lou Dupont
#  http://www.systemical.com/
#
# Makefile for releasing the project
#

## <<< CUSTOMIZE HERE
PRJ=rb_playlists_auto_export
PKG=rb-playlists-auto-export
DOC=http://www.systemical.com/doc/opensource/rb_playlists_auto_export
## >>>

VERSION:=`cat VERSION`

DEFAULT_DISTRO=lucid

ifeq ($(DIST),)
	DIST=${DEFAULT_DISTRO}
endif

all:
	@echo "Version: ${VERSION}"
	@echo "Options:"
	@echo "  clean, orig"
	@echo "  ppa, pb, up"

clean:
	@echo "Cleaning - Version: ${VERSION}"
	@rm -r -f /tmp/$(PRJ)
	
orig:
	@echo "* Preparing for packaging -- Version: ${VERSION}, Distribution: ${DIST}"
	@echo "-------------------------"
	@echo ""
	@echo "mkdir directories ( /tmp/$(PRJ)/$(PRJ)-$(VERSION) )"
	@mkdir -p "/tmp/$(PRJ)"
	@mkdir -p "/tmp/$(PRJ)/$(PRJ)-$(VERSION)"
	
	@echo "Copying package folder"
	@rsync -r --exclude=*.git* src/ "/tmp/$(PRJ)/$(PRJ)-$(VERSION)"

	@echo "Copying debian folder"
	@rsync -r --exclude=*.svn* packages/debian "/tmp/$(PRJ)/$(PRJ)-$(VERSION)"
	@echo "Copying packaging makefile"
	@cp makefile "/tmp/$(PRJ)/makefile"
	@cp VERSION "/tmp/$(PRJ)/VERSION"
		
	@echo "Adjusting debian/changelog to DIST & VERSION"
	@cat packages/debian/changelog | sed "s/_DIST_/${DIST}/g" | sed "s/_VERSION_/${VERSION}/g | sed "s/_PRJ_/${PRJ}/g" > "/tmp/${PRJ}/${PRJ}-${VERSION}/debian/changelog"
	@cat packages/debian/control   | sed "s/_DIST_/${DIST}/g" | sed "s/_VERSION_/${VERSION}/g | sed "s/_PRJ_/${PRJ}/g | sed "s/_PKG_/${PKG}/g | sed "s/_DOC_/${DOC}/g" > "/tmp/${PRJ}/${PRJ}-${VERSION}/debian/control"
	
	@echo "** SUCCESS: folder ready: /tmp/$(PRJ)"
	@echo "*** DON'T FORGET TO UPDATE debian/changelog ***"

	@echo "!!! Have you updated debian/changelog ?"

	@echo "Running 'debuild'"
	@cd "/tmp/$(PRJ)/$(PRJ)-$(VERSION)" && debuild -S
	
up:
	@echo "UPLOADING TO PPA"
	@cd "/tmp/$(PRJ)/" && dput ppa:jldupont/jldupont *.changes


pb:
	@echo " ----------------------------- "
	@echo " RUNNING PBUILDER "
	@cd "/tmp/$(PRJ)/" && sudo DIST=${DIST} pbuilder build *.dsc

.PHONY: orig pb
