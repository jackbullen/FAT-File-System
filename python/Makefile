SCRIPTS = diskinfo.py disklist.py diskget.py diskput.py
TARGETS = $(SCRIPTS:.py=)

all: $(TARGETS)

%: %.py
	@echo "Making $@"
	cp $< $@
	chmod u+x $@

clean:
	rm -rf $(TARGETS)

.PHONY: all clean