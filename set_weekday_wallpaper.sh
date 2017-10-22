#!/bin/bash
# This command will set the wallpaper based on the chosen weekday template
# using feh(1) as the setter.

# The file names for templates I've chosen: ${weekday}-${template_name}.${ext}
# in all lower-case and (hopefully) all *.jpg files. eg.
#   friday-blue.jpg
# Also note the hyphen separation instead of underscore or space.

# If a command line argument is supplied, assume it's the template name. eg.
#   ./set_weekday_wallpaper.sh red
# should attempt to set the wallpaper to friday-red.jpg on Fridays.


# Location of directory containing the at least one wallpaper for each day of
# the week
readonly WEEKDAY_WALLPAPERS_DIR="$HOME/Pictures/Wallpapers/Weekdays"

# The default for ${template} in the filename
readonly DEFAULT_TEMPLATE='blue'
template="${DEFAULT_TEMPLATE}"

# The file extension is a variable in case other templates have different
# extensions in the future. Fow now, it does nothing.
readonly FILEXT='jpg'


function fatal() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S%z')]: $@" >&2
  exit 1
}

function get_day_of_week() {
  case "$(date +'%w')" in
    0) echo 'sunday' ;;
    1) echo 'monday' ;;
    2) echo 'tuesday' ;;
    3) echo 'wednesday' ;;
    4) echo 'thursday' ;;
    5) echo 'friday' ;;
    6) echo 'saturday' ;;
  esac
}

function print_filename() {
  echo "$(get_day_of_week)-${template}.${FILEXT}"
}

function main() {
  # Check if an optional template was specified
  if [[ $# -gt 0 ]]; then
    template="$1"
  fi

  # Build the full path to the wallpaper
  local wallpaper_path="${WEEKDAY_WALLPAPERS_DIR}/$(print_filename)"

  # Set wallpaper
  if [[ -x "$(which feh)" ]]; then
    if [[ ! -f "${wallpaper_path}" ]]; then
      fatal "$0: Bad wallpaper path: ${wallpaper_path}"
    fi
    feh --bg-fill "${wallpaper_path}"
  else
    fatal "$0: Unable to find feh"
  fi
}

main "$@"
