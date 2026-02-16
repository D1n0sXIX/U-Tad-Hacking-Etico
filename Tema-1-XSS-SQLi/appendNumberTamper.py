#!/usr/bin/env python

from lib.core.enums import PRIORITY
__priority__ = PRIORITY.LOWEST

def dependencies():
	pass
def tamper(payload, **kwargs):
	if payload:
		payload = payload + "and 1=1"
	return payload
