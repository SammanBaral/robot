import qrcode

# # Define the data for each QR code
# data_hello = "tribhuwankoinfo"
# data_bye = "martinkoinfo"
# data_turn="endMaTurn"

# # Generate QR code for say_hello
# qr_hello = qrcode.QRCode(
#     version=1,
#     error_correction=qrcode.constants.ERROR_CORRECT_L,
#     box_size=10,
#     border=4,
# )
# qr_hello.add_data(data_hello)
# qr_hello.make(fit=True)

# img_hello = qr_hello.make_image(fill='black', back_color='white')
# img_hello.save("tribhuwan.png")

# # Generate QR code for say_bye
# qr_bye = qrcode.QRCode(
#     version=1,
#     error_correction=qrcode.constants.ERROR_CORRECT_L,
#     box_size=10,
#     border=4,
# )
# qr_bye.add_data(data_bye)
# qr_bye.make(fit=True)

# img_bye = qr_bye.make_image(fill='black', back_color='white')
# img_bye.save("martin.png")

# qr_turn = qrcode.QRCode(
#     version=1,
#     error_correction=qrcode.constants.ERROR_CORRECT_L,
#     box_size=10,
#     border=4,
# )
# qr_turn.add_data(data_turn)
# qr_turn.make(fit=True)

# img_turn = qr_turn.make_image(fill='black', back_color='white')
# img_turn.save("turn.png")


# Define the data for each QR code
artifact_ko_info = "hitlerkoinfo"
data_turn="ending"

# Generate QR code for say_hello
qr_hello = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr_hello.add_data(data_turn)
qr_hello.make(fit=True)

img_hello = qr_hello.make_image(fill='black', back_color='white')
img_hello.save("ending.png")

# Generate QR code for say_bye
qr_bye = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr_bye.add_data(artifact_ko_info)
qr_bye.make(fit=True)

img_bye = qr_bye.make_image(fill='black', back_color='white')
img_bye.save("hitler.png")

# qr_turn = qrcode.QRCode(
#     version=1,
#     error_correction=qrcode.constants.ERROR_CORRECT_L,
#     box_size=10,
#     border=4,
# )
# qr_turn.add_data(data_turn)
# qr_turn.make(fit=True)

# img_turn = qr_turn.make_image(fill='black', back_color='white')
# img_turn.save("turn.png")