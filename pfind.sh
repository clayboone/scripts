#!/bin/bash
exec ps -fep $(pgrep -fi $@)
