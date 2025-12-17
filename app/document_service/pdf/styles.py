from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

styles = getSampleStyleSheet()

styles["Title"].alignment = TA_CENTER
styles["Normal"].fontSize = 9

RIGHT_ALIGN = TA_RIGHT
CENTER_ALIGN = TA_CENTER
