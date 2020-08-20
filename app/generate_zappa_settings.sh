#!/bin/bash
envsubst < zappa_settings.json.tpl > zappa_settings.json
source /venv/bin/activate