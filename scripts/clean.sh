#!/usr/bin/env bash

# Pick a folder, delete ZIP files permanently, then gather media into folders.

set -u

VIDEO_FOLDER_NAME="Video Files"
IMAGE_FOLDER_NAME="Image Files"

choose_folder() {
  osascript <<'APPLESCRIPT'
try
  set chosenFolder to choose folder with prompt "Choose a folder. ZIP files inside it will be permanently deleted, videos moved to Video Files, and images moved to Image Files."
  POSIX path of chosenFolder
on error number -128
  return ""
end try
APPLESCRIPT
}

ask_repeat() {
  osascript <<'APPLESCRIPT'
try
  set answer to button returned of (display dialog "Do you want to process another folder?" buttons {"Exit", "Choose Another Folder"} default button "Choose Another Folder" cancel button "Exit")
  if answer is "Choose Another Folder" then
    return "yes"
  else
    return "no"
  end if
on error number -128
  return "no"
end try
APPLESCRIPT
}

unique_destination() {
  local dest_dir="$1"
  local filename="$2"
  local base="$filename"
  local ext=""
  local candidate
  local counter=1

  if [[ "$filename" == *.* && "$filename" != .* ]]; then
    base="${filename%.*}"
    ext=".${filename##*.}"
  fi

  candidate="$dest_dir/$filename"
  while [[ -e "$candidate" ]]; do
    candidate="$dest_dir/${base} (${counter})${ext}"
    counter=$((counter + 1))
  done

  printf '%s\n' "$candidate"
}

move_matching_files() {
  local source_dir="$1"
  local dest_dir="$2"
  local kind="$3"
  shift 3

  local moved=0
  local file
  local filename
  local destination
  local ext
  local find_args=()
  local last_arg

  for ext in "$@"; do
    find_args+=( -iname "*.$ext" -o )
  done
  last_arg=$((${#find_args[@]} - 1))
  unset "find_args[$last_arg]"

  while IFS= read -r -d '' file; do
    filename="$(basename "$file")"
    destination="$(unique_destination "$dest_dir" "$filename")"
    mv "$file" "$destination"
    moved=$((moved + 1))
  done < <(
    find "$source_dir" \
      -path "$dest_dir" -prune -o \
      -path "$source_dir/$VIDEO_FOLDER_NAME" -prune -o \
      -path "$source_dir/$IMAGE_FOLDER_NAME" -prune -o \
      -type f \( "${find_args[@]}" \) -print0
  )

  printf 'Moved %d %s file(s).\n' "$moved" "$kind"
}

delete_empty_folders() {
  local source_dir="$1"
  local video_dir="$source_dir/$VIDEO_FOLDER_NAME"
  local image_dir="$source_dir/$IMAGE_FOLDER_NAME"
  local deleted_ds_store
  local deleted=0
  local pass_deleted=0
  local folder

  deleted_ds_store="$(
    find "$source_dir" -type f -name ".DS_Store" -print -delete | wc -l | tr -d ' '
  )"

  while true; do
    pass_deleted=0

    while IFS= read -r -d '' folder; do
      if rmdir "$folder" 2>/dev/null; then
        pass_deleted=$((pass_deleted + 1))
      fi
    done < <(
      find "$source_dir" -depth -mindepth 1 -type d \
        ! -path "$video_dir" \
        ! -path "$image_dir" \
        -print0
    )

    deleted=$((deleted + pass_deleted))

    if [[ "$pass_deleted" -eq 0 ]]; then
      break
    fi
  done

  printf 'Deleted %s Finder metadata file(s).\n' "$deleted_ds_store"
  printf 'Deleted %d empty folder(s).\n' "$deleted"
}

process_folder() {
  local folder="$1"
  local video_dir
  local image_dir
  local deleted_zips

  folder="${folder%/}"
  video_dir="$folder/$VIDEO_FOLDER_NAME"
  image_dir="$folder/$IMAGE_FOLDER_NAME"

  mkdir -p "$video_dir" "$image_dir"

  deleted_zips="$(
    find "$folder" -type f -iname "*.zip" -print -delete | wc -l | tr -d ' '
  )"

  printf '\nProcessed: %s\n' "$folder"
  printf 'Permanently deleted %s ZIP file(s).\n' "$deleted_zips"

  move_matching_files "$folder" "$video_dir" "video" \
    3gp avi flv m2ts m4v mkv mov mp4 mpeg mpg mts webm wmv

  move_matching_files "$folder" "$image_dir" "image" \
    arw avif bmp cr2 cr3 dng gif heic heif jpeg jpg nef png raf raw rw2 tif tiff webp

  delete_empty_folders "$folder"
}

while true; do
  selected_folder="$(choose_folder)"

  if [[ -z "$selected_folder" ]]; then
    echo "No folder selected. Exiting."
    exit 0
  fi

  process_folder "$selected_folder"

  if [[ "$(ask_repeat)" != "yes" ]]; then
    echo "Done."
    exit 0
  fi
done
