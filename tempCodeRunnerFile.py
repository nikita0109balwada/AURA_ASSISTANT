def image_upload():
    global generate_image_mode
    generate_image_mode = not generate_image_mode
    if generate_image_mode:
        display_message("Generating images", "assistant")
    else:
        display_message("🖼️ Image mode OFF. Back to normal chat.", "assistant")
