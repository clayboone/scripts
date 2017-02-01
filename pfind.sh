#!/bin/bash
exec ps -fp $(pgrep -i $@)
