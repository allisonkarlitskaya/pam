# Makefile for source rpm: pam
# $Id$
NAME := pam
SPECFILE = $(firstword $(wildcard *.spec))

include ../common/Makefile.common
