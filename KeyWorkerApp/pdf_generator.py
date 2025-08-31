import os
import sys
import webbrowser
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ==============================================================================
# FONT REGISTRATION FOR EMOJIS
# ==============================================================================
EMOJI_FONT_FOUND = False
try:
    # Try Apple Color Emoji for macOS
    pdfmetrics.registerFont(TTFont('AppleColorEmoji', '/System/Library/Fonts/Apple Color Emoji.ttc'))
    EMOJI_FONT = 'AppleColorEmoji'
    EMOJI_FONT_FOUND = True
except (OSError, IOError, Exception) as e:
    try:
        # Try Segoe UI Emoji for Windows 10+
        pdfmetrics.registerFont(TTFont('SegoeUIEmoji', 'C:/Windows/Fonts/seguiemj.ttf'))
        EMOJI_FONT = 'SegoeUIEmoji'
        EMOJI_FONT_FOUND = True
    except (OSError, IOError, Exception) as e:
        try:
            # Try alternative Windows emoji font paths
            pdfmetrics.registerFont(TTFont('SegoeUIEmoji', 'C:/Windows/Fonts/seguisym.ttf'))
            EMOJI_FONT = 'SegoeUIEmoji'
            EMOJI_FONT_FOUND = True
        except (OSError, IOError, Exception) as e:
            try:
                # Try Noto Color Emoji as fallback
                pdfmetrics.registerFont(TTFont('NotoColorEmoji', 'C:/Windows/Fonts/NotoColorEmoji.ttf'))
                EMOJI_FONT = 'NotoColorEmoji'
                EMOJI_FONT_FOUND = True
            except (OSError, IOError, Exception) as e:
                print("No emoji font found. Using text alternatives.")
                EMOJI_FONT = 'Helvetica'


# ==============================================================================
# HELPER CLASS FOR DRAWING CHECKBOXES
# ==============================================================================
class Checkbox(Paragraph):
    def __init__(self, text, checked=False):
        super().__init__(text, style=getSampleStyleSheet()['BodyText'])
        self.checked = checked
        self.style = self.style
        self.style.fontSize = 9
        self.style.leftIndent = 15

    def draw(self):
        super().draw()
        self.canv.saveState()
        self.canv.translate(0, 2)
        self.canv.rect(0, 0, 9, 9)
        if self.checked:
            self.canv.setFont("Helvetica-Bold", 9)
            self.canv.drawCentredString(4.5, 2, "✓")
        self.canv.restoreState()

# ==============================================================================
# MAIN PDF GENERATION FUNCTION
# ==============================================================================
def generate_pdf(data):
    try:
        downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
        os.makedirs(downloads_folder, exist_ok=True)
        user_name = data.get('service_user_name', 'user').replace(' ', '_')
        month = data.get('month', 'month')
        year = data.get('year', 'year')
        file_name = f"Key_Worker_Form_{user_name}_{month}_{year}.pdf"
        file_path = os.path.join(downloads_folder, file_name)

        doc = SimpleDocTemplate(
            file_path, pagesize=A4,
            rightMargin=0.75*inch, leftMargin=0.75*inch,
            topMargin=0.75*inch, bottomMargin=0.75*inch
        )

        story = []
        styles = getSampleStyleSheet()
        p_style = styles['BodyText']
        p_style.fontSize = 9
        p_style_indented = ParagraphStyle(name='Indented', parent=p_style, leftIndent=20)
        h1_style = ParagraphStyle(name='H1', parent=styles['h2'], spaceBefore=12, spaceAfter=6)
        
        # Create header title style
        title_style = ParagraphStyle(name='Title', parent=styles['Title'], fontSize=16, spaceAfter=12, alignment=0)  # Left aligned
        facility_style = ParagraphStyle(name='Facility', parent=styles['Title'], fontSize=16, spaceAfter=12, alignment=2)  # Right aligned

        # ======================================================================
        # BUILD THE STORY (ALL CONTENT)
        # ======================================================================
        
        # --- Header with Form Title and Facility Name ---
        header_title_data = [
            [Paragraph('<b>Key Worker Records</b>', title_style), Paragraph('<b>Alyson House</b>', facility_style)]
        ]
        header_title_table = Table(header_title_data, colWidths=[3.5*inch, 3.5*inch])
        header_title_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6)
        ]))
        story.append(header_title_table)
        story.append(Spacer(1, 0.2 * inch))
        
        # --- User Info Table ---
        header_data = [
            [Paragraph('<b>Service User:</b>', p_style), Paragraph(data.get('service_user_name', ''), p_style), Paragraph('<b>DOB:</b>', p_style), Paragraph(data.get('dob', ''), p_style)],
            [Paragraph('<b>Key Worker:</b>', p_style), Paragraph(data.get('key_worker_name', ''), p_style), Paragraph('<b>Date and Time of Session:</b>', p_style), Paragraph(data.get('session_datetime', ''), p_style)]
        ]
        header_table = Table(header_data, colWidths=[1.5*inch, 2.0*inch, 1.8*inch, 1.7*inch])
        header_table.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 6)]))
        story.append(header_table)
        story.append(Spacer(1, 0.25 * inch))

        # --- MY HEALTH Section ---
        story.append(Paragraph("MY HEALTH", h1_style))
        
        appointments_from_db = data.get('appointments', [])
        table_data = [[Paragraph(f'<b>{col}</b>', p_style) for col in ['Appointment', 'Last Seen', 'Next Due', 'Booked (Yes/No)']]]
        if not appointments_from_db:
            table_data.append([Paragraph("No appointments added for this month.", p_style), '', '', ''])
        else:
            for appt in appointments_from_db:
                table_data.append([Paragraph(appt.get('name', ''), p_style), Paragraph(appt.get('last_seen', ''), p_style), Paragraph(appt.get('next_due', ''), p_style), Paragraph(appt.get('booked', ''), p_style)])
        
        appointments_table = Table(table_data, colWidths=[1.7*inch, 1.8*inch, 1.8*inch, 1.7*inch])
        appointments_table.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 6)]))
        story.append(appointments_table)
        story.append(Spacer(1, 0.2 * inch))
        
        health_checks_data = [
            [Paragraph(f'<b>LAST WEIGHT:</b> {data.get("weight", "")}', p_style), None, None, Paragraph(f'<b>BLOOD PRESSURE:</b> {data.get("bp", "")}', p_style)],
            [Paragraph(f'<b>WEIGHT/BP COMMENTS:</b> {data.get("weight_bp_comments", "")}', p_style), None, None, None],
            [Paragraph('Do I have any concerns with my Health, Fitness or Diet?', p_style), Checkbox("YES", data.get('health_concerns') == 'Yes'), Checkbox("NO", data.get('health_concerns') == 'No'), Paragraph(f"<b>COMMENTS:</b> {data.get('health_concerns_comments', '')}", p_style)],
            [Paragraph('Do I need to have my finger and toe nails cut?', p_style), Checkbox("YES", data.get('nails_check') == 'Yes'), Checkbox("NO", data.get('nails_check') == 'No'), Paragraph(f"<b>SESSION DATE:</b> {data.get('nails_date', '')} <b>COMMENTS:</b> {data.get('nails_comments', '')}", p_style)],
            [Paragraph('Do I need a hair cut?', p_style), Checkbox("YES", data.get('hair_check') == 'Yes'), Checkbox("NO", data.get('hair_check') == 'No'), Paragraph(f"<b>SESSION DATE:</b> {data.get('hair_date', '')} <b>COMMENTS:</b> {data.get('hair_comments', '')}", p_style)],
            [Paragraph('Are my MAR Sheets accurate and up to date?', p_style), Checkbox("YES", data.get('mar_sheets_check') == 'Yes'), Checkbox("NO", data.get('mar_sheets_check') == 'No'), Paragraph(f"<b>COMMENTS:</b> {data.get('mar_sheets_comments', '')}", p_style)]
        ]
        health_checks_table = Table(health_checks_data, colWidths=[2.8*inch, 0.8*inch, 0.8*inch, 2.6*inch])
        health_checks_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black), 
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), 
            ('LEFTPADDING', (0,0), (-1,-1), 6), 
            ('MINHEIGHT', (0,0), (-1,-1), 0.4*inch),
            # Span cells for weight/BP row and comments row
            ('SPAN', (0,0), (2,0)),  # Weight spans first 3 columns
            ('SPAN', (0,1), (3,1))   # Weight comments spans all 4 columns
        ]))
        story.append(health_checks_table)
        story.append(Spacer(1, 0.25 * inch))

        # --- MY FINANCES Section ---
        story.append(Paragraph("MY FINANCES", h1_style))
        finances_data = [
            [Paragraph('How much money do I have in my cash box?', p_style), Paragraph(f"£ {data.get('finance_cash_box', '')}", p_style), None],
            [Paragraph('Does it need topping up (cash should always be above £30.00)?', p_style), Checkbox("YES", data.get('finance_top_up') == 'Yes'), Checkbox("NO", data.get('finance_top_up') == 'No')],
            [Paragraph('If YES, how much shall I take out?', p_style), Paragraph(f"£ {data.get('finance_take_out', '')}", p_style), None],
            [Paragraph('<b>If YES, plan this and enter it in to the diary.</b>', p_style), None, None],
            [Paragraph('<b>Date and Time</b>', p_style), Paragraph(data.get('finance_diary_datetime', ''), p_style), None],
            [Paragraph('<b>Supporting Staff</b>', p_style), Paragraph(data.get('finance_diary_staff', ''), p_style), None]
        ]
        finances_table = Table(finances_data, colWidths=[3.5*inch, 2.5*inch, 1.0*inch], rowHeights=0.3*inch)
        finances_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('SPAN', (1,0), (2,0)), ('SPAN', (1,2), (2,2)), ('SPAN', (0,3), (2,3)),
            ('SPAN', (1,4), (2,4)), ('SPAN', (1,5), (2,5))
        ]))
        story.append(finances_table)
        story.append(Spacer(1, 0.25 * inch))

        # --- PERSONAL SHOPPING Section ---
        story.append(Paragraph("PERSONAL SHOPPING", h1_style))
        shopping_data = [
            [Paragraph('1) Do I have enough toiletries?', p_style), Checkbox("YES", data.get('shop_q1_toiletries') == 'Yes'), Checkbox("NO", data.get('shop_q1_toiletries') == 'No'), Paragraph(f"{data.get('shop_q1_comments', '')}", p_style)],
            [Paragraph('2) Are all my clothes and shoes in good repair?', p_style), Checkbox("YES", data.get('shop_q2_clothes') == 'Yes'), Checkbox("NO", data.get('shop_q2_clothes') == 'No'), Paragraph(f"{data.get('shop_q2_comments', '')}", p_style)],
            [Paragraph('3) Do I need to or would I like to buy any personal items?', p_style), Checkbox("YES", data.get('shop_q3_personal_items') == 'Yes'), Checkbox("NO", data.get('shop_q3_personal_items') == 'No'), Paragraph(f"{data.get('shop_q3_comments', '')}", p_style)]
        ]
        shopping_table = Table(shopping_data, colWidths=[3.5*inch, 0.75*inch, 0.75*inch, 2.0*inch], rowHeights=0.3*inch)
        shopping_table.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 6)]))
        story.append(shopping_table)
        story.append(Spacer(1, 0.25 * inch))

        # --- SUPPORT PLANS Section ---
        story.append(Paragraph("UPDATING MY SUPPORT PLANS", h1_style))
        instruction_text = "The answer to the below questions should be YES. Key-workers must do the following:<br/>• Review all the below records and ensure they are current and correct.<br/>• Ensure I have been involved in any changes which have been made.<br/>• Ensure I am in agreement in any changes or that they are at least made in my best interest."
        story.append(Paragraph(instruction_text, p_style))
        story.append(Spacer(1, 0.1 * inch))
        support_plan_data = [
            [Paragraph('<b>1. MY CAREDOCS SUPPORT PLAN</b>', p_style), None, None],
            [Paragraph('a. CONTACTS', p_style_indented), Checkbox("YES", data.get('caredocs_contacts') == 'Yes'), Checkbox("NO", data.get('caredocs_contacts') == 'No')],
            [Paragraph('b. CARE PLAN', p_style_indented), Checkbox("YES", data.get('caredocs_careplan') == 'Yes'), Checkbox("NO", data.get('caredocs_careplan') == 'No')],
            [Paragraph('c. MEDICATION', p_style_indented), Checkbox("YES", data.get('caredocs_meds') == 'Yes'), Checkbox("NO", data.get('caredocs_meds') == 'No')],
            [Paragraph('d. BODY MAP', p_style_indented), Checkbox("YES", data.get('caredocs_bodymap') == 'Yes'), Checkbox("NO", data.get('caredocs_bodymap') == 'No')],
            [Paragraph('e. CHARTS', p_style_indented), Checkbox("YES", data.get('caredocs_charts') == 'Yes'), Checkbox("NO", data.get('caredocs_charts') == 'No')],
            [Paragraph('<b>2. MY HEALTH ACTION PLAN/FILE</b>', p_style), Checkbox("YES", data.get('health_plan_file') == 'Yes'), Checkbox("NO", data.get('health_plan_file') == 'No')]
        ]
        support_plan_table = Table(support_plan_data, colWidths=[5.0*inch, 1*inch, 1*inch], rowHeights=0.3*inch)
        support_plan_table.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black), ('SPAN', (0,0), (-1,0)), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 6)]))
        story.append(support_plan_table)
        story.append(Spacer(1, 0.1 * inch))

        actions_data = [[Paragraph('If "NO" to any of the above what actions are required?', p_style)], [Paragraph(data.get('actions_required', '').replace('\n', '<br/>'), p_style)]]
        actions_table = Table(actions_data, colWidths=[7.0*inch], rowHeights=[0.3*inch, 0.6*inch])
        actions_table.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black), ('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 6), ('TOPPADDING', (0,0), (-1,-1), 6)]))
        story.append(actions_table)
        story.append(Spacer(1, 0.25 * inch))

        # --- FAMILY COMMUNICATION Section ---
        story.append(Paragraph("MONTHLY COMMUNICATION WITH FAMILY/NOK", h1_style))
        family_comm_data = [
            [Paragraph('Monthly phone call to my family / NOK made?', p_style), Checkbox("YES", data.get('family_comm_made') == 'Yes'), Checkbox("NO", data.get('family_comm_made') == 'No')],
            [Paragraph(f"<b>If YES enter DATE AND TIME:</b> {data.get('family_comm_datetime', '')}", p_style), None, None],
            [Paragraph(f"<b>IF NO... PLEASE STATE REASON:</b><br/>{data.get('family_comm_reason', '').replace(chr(10), '<br/>')}", p_style), None, None],
            [Paragraph(f"<b>ISSUES/CONCERNS/ACTIONS:</b><br/>{data.get('family_comm_issues', '').replace(chr(10), '<br/>')}", p_style), None, None]
        ]
        family_comm_table = Table(family_comm_data, colWidths=[5.0*inch, 1*inch, 1*inch], rowHeights=[0.3*inch, 0.3*inch, 0.6*inch, 0.6*inch])
        family_comm_table.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black), ('SPAN', (0,1), (-1,1)), ('SPAN', (0,2), (-1,2)), ('SPAN', (0,3), (-1,3)), ('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 6), ('TOPPADDING', (0,0), (-1,-1), 6)]))
        story.append(family_comm_table)
        story.append(Spacer(1, 0.25 * inch))

        # --- FEELINGS AND GOALS Section ---
        story.append(Paragraph("HOW ARE YOU FEELING?", h1_style))
        
        # Get selected icons from data
        selected_feeling_icons = data.get('feeling_icons_selected', '').split(',') if data.get('feeling_icons_selected') else []
        selected_care_icons = data.get('care_icons_selected', '').split(',') if data.get('care_icons_selected') else []
        
        # Create 2x2 grid of feeling icons 
        feeling_icons_data = [
            [
                [_create_icon_image("Happy Emoji.png", selected_feeling_icons, "Happy", width=0.5*inch, height=0.5*inch), Paragraph("Happy", p_style)],
                [_create_icon_image("Sad emoji.jpg", selected_feeling_icons, "Sad", width=0.5*inch, height=0.5*inch), Paragraph("Sad", p_style)]
            ],
            [
                [_create_icon_image("thumbs up emoji.jpg", selected_feeling_icons, "Good", width=0.5*inch, height=0.5*inch), Paragraph("Good", p_style)],
                [_create_icon_image("thumbds down emoji.png", selected_feeling_icons, "Not Good", width=0.5*inch, height=0.5*inch), Paragraph("Not Good", p_style)]
            ]
        ]
        
        # Create left column with icons and right column with response
        feeling_layout_data = [
            [
                Table(feeling_icons_data, colWidths=[1.5*inch, 1.5*inch], rowHeights=[1.0*inch, 1.0*inch]),
                Paragraph(f"<b>Record Response Here:</b><br/>{data.get('feeling_response', '').replace(chr(10), '<br/>')}", p_style)
            ]
        ]
        
        feeling_table = Table(feeling_layout_data, colWidths=[3.0*inch, 4.0*inch], rowHeights=2.0*inch)
        feeling_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black), 
            ('VALIGN', (0,0), (-1,-1), 'TOP'), 
            ('LEFTPADDING', (0,0), (-1,-1), 6), 
            ('TOPPADDING', (0,0), (-1,-1), 6)
        ]))
        
        # Apply selection highlights for feeling icons
        feeling_labels = ["Happy", "Sad", "Good", "Not Good"]
        icon_positions = [(0, 0, 0, 0), (0, 0, 0, 1), (0, 0, 1, 0), (0, 0, 1, 1)]
        for i, label in enumerate(feeling_labels):
            if label in selected_feeling_icons:
                row, col = icon_positions[i][2], icon_positions[i][3] 
                # Note: This is a simplified approach. For more complex highlighting,
                # you might need to create custom cell backgrounds
        
        story.append(feeling_table)
        
        # No spacing - go directly to next section
        story.append(Paragraph("ARE YOU HAPPY WITH YOUR CARE AND SUPPORT?", h1_style))
        
        # Create horizontal row of care icons
        care_icons_row = [
            [_create_icon_image("Art Work.jpg", selected_care_icons, "Art", width=0.4*inch, height=0.4*inch), Paragraph("Art", p_style)],
            [_create_icon_image("Healthy-Food-Choices.png", selected_care_icons, "Food", width=0.4*inch, height=0.4*inch), Paragraph("Food", p_style)],
            [_create_icon_image("Medicine.jpeg", selected_care_icons, "Medicine", width=0.4*inch, height=0.4*inch), Paragraph("Medicine", p_style)],
            [_create_icon_image("Shower.jpg", selected_care_icons, "Shower", width=0.4*inch, height=0.4*inch), Paragraph("Shower", p_style)],
            [_create_icon_image("Happy Emoji.png", selected_care_icons, "Happy", width=0.4*inch, height=0.4*inch), Paragraph("Happy", p_style)],
            [_create_icon_image("Sad emoji.jpg", selected_care_icons, "Sad", width=0.4*inch, height=0.4*inch), Paragraph("Sad", p_style)]
        ]
        
        care_layout_data = [
            [Table([care_icons_row], colWidths=[1.15*inch]*6, rowHeights=[1.0*inch])],
            [Paragraph(f"<b>Record Response Here:</b><br/>{data.get('happy_response', '').replace(chr(10), '<br/>')}", p_style)]
        ]
        
        happy_table = Table(care_layout_data, colWidths=[7.0*inch], rowHeights=[1.0*inch, 1.0*inch])
        happy_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black), 
            ('VALIGN', (0,0), (-1,-1), 'TOP'), 
            ('LEFTPADDING', (0,0), (-1,-1), 6), 
            ('TOPPADDING', (0,0), (-1,-1), 6)
        ]))
        
        story.append(happy_table)
        story.append(Spacer(1, 0.25 * inch))

        story.append(Paragraph("ANY OTHER ACTIONS / NOTES:", h1_style))
        notes_data = [[Paragraph(f"<b>Record Response Here:</b><br/>{data.get('other_notes', '').replace(chr(10), '<br/>')}", p_style)]]
        notes_table = Table(notes_data, colWidths=[7.0*inch], rowHeights=2.0*inch)
        notes_table.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black), ('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 6), ('TOPPADDING', (0,0), (-1,-1), 6)]))
        story.append(notes_table)
        story.append(Spacer(1, 0.5 * inch))

        # --- SIGNATURE Section ---
        signature_data = [
            [Paragraph("<b>Service User</b>", p_style), Paragraph(data.get('service_user_name', ''), p_style), Paragraph("<b>Key Worker</b>", p_style), Paragraph(data.get('key_worker_name', ''), p_style)],
            [Paragraph("<b>Date</b>", p_style), Paragraph(data.get('session_datetime', ''), p_style), Paragraph("<b>Date</b>", p_style), Paragraph(data.get('session_datetime', ''), p_style)]
        ]
        signature_table = Table(signature_data, colWidths=[1.2*inch, 2.3*inch, 1.2*inch, 2.3*inch], rowHeights=0.5*inch)
        signature_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'BOTTOM'), ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('LINEABOVE', (1,1), (1,1), 1, colors.black), ('LINEABOVE', (3,1), (3,1), 1, colors.black)
        ]))
        story.append(signature_table)

        # Build the document
        doc.build(story)

        if sys.platform == "darwin":
            os.system(f'open "{file_path}"')
        else:
            webbrowser.open(file_path)

        return True, None
    except Exception as e:
        print(f"Error in PDF generation: {e}")
        return False, str(e)

def _create_icon_image(icon_filename, selected_icons, icon_label, width=0.8*inch, height=0.8*inch):
    """Create an image with selection highlight if the icon was selected"""
    try:
        # Get the directory where this script is located  
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "images", icon_filename)
        
        if os.path.exists(icon_path):
            img = Image(icon_path, width=width, height=height)
            
            # If this icon was selected, we'll highlight it in the table styling
            return img
        else:
            # Fallback to text if image not found
            return icon_label
    except Exception as e:
        print(f"Error loading icon {icon_filename}: {e}")
        return icon_label

def _get_icon_cell_style(selected_icons, icon_label):
    """Get the table cell style for an icon based on whether it's selected"""
    if icon_label in selected_icons:
        return ('BACKGROUND', colors.lightgreen)
    else:
        return ('BACKGROUND', colors.white)
