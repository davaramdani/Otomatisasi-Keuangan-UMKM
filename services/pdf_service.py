import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime

PINK_DARK  = colors.HexColor('#C2185B')
PINK_MID   = colors.HexColor('#E91E8C')
PINK_LIGHT = colors.HexColor('#FCE4EC')
PINK_PALE  = colors.HexColor('#FFF0F7')
GREY_DARK  = colors.HexColor('#424242')
GREY_MID   = colors.HexColor('#757575')
GREY_LIGHT = colors.HexColor('#F5F5F5')
WHITE      = colors.white

def generate_invoice(data: dict) -> str:
    os.makedirs("output/invoices", exist_ok=True)
    filename = f"output/invoices/{data['invoice_no']}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4,
        rightMargin=1.8*cm, leftMargin=1.8*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm)
    elements = []

    brand_style     = ParagraphStyle('brand', fontSize=24, fontName='Helvetica-Bold', textColor=PINK_DARK, leading=28)
    tagline_style   = ParagraphStyle('tagline', fontSize=9, fontName='Helvetica', textColor=GREY_MID)
    inv_title_style = ParagraphStyle('inv_title', fontSize=26, fontName='Helvetica-Bold', textColor=WHITE, alignment=2, leading=30)
    inv_no_style    = ParagraphStyle('inv_no', fontSize=10, fontName='Helvetica', textColor=colors.HexColor('#FFCDD2'), alignment=2)
    label_style     = ParagraphStyle('label', fontSize=8, fontName='Helvetica-Bold', textColor=GREY_MID)
    value_style     = ParagraphStyle('value', fontSize=10, fontName='Helvetica-Bold', textColor=GREY_DARK)
    th_style        = ParagraphStyle('th', fontSize=9, fontName='Helvetica-Bold', textColor=WHITE, alignment=1)
    td_style        = ParagraphStyle('td', fontSize=10, fontName='Helvetica', textColor=GREY_DARK)
    td_right        = ParagraphStyle('td_r', fontSize=10, fontName='Helvetica', textColor=GREY_DARK, alignment=2)
    td_center       = ParagraphStyle('td_c', fontSize=10, fontName='Helvetica', textColor=GREY_DARK, alignment=1)
    sub_label       = ParagraphStyle('sub_l', fontSize=10, fontName='Helvetica', textColor=GREY_MID, alignment=2)
    sub_value       = ParagraphStyle('sub_v', fontSize=10, fontName='Helvetica', textColor=GREY_DARK, alignment=2)
    tot_label       = ParagraphStyle('tot_l', fontSize=12, fontName='Helvetica-Bold', textColor=WHITE, alignment=2)
    tot_value       = ParagraphStyle('tot_v', fontSize=12, fontName='Helvetica-Bold', textColor=WHITE, alignment=2)
    footer_left     = ParagraphStyle('fl', fontSize=9, fontName='Helvetica', textColor=GREY_MID)
    footer_right    = ParagraphStyle('fr', fontSize=9, fontName='Helvetica', textColor=PINK_DARK, alignment=2)
    note_style      = ParagraphStyle('note', fontSize=8, fontName='Helvetica-Oblique', textColor=GREY_MID, alignment=1, spaceBefore=4)

    header_left  = Table([[Paragraph("Zee Zee Dessert", brand_style)],[Paragraph("Homemade Desserts - Jakarta", tagline_style)],[Paragraph("IG: @zeezeedessert", tagline_style)]], colWidths=[10*cm])
    header_right = Table([[Paragraph("INVOICE", inv_title_style)],[Paragraph(f"# {data['invoice_no']}", inv_no_style)]], colWidths=[7.4*cm])
    header_left.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),WHITE),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),8),('LEFTPADDING',(0,0),(-1,-1),8)]))
    header_right.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),PINK_DARK),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),('BOTTOMPADDING',(0,0),(-1,-1),12),('LEFTPADDING',(0,0),(-1,-1),8)]))
    header_outer = Table([[header_left, header_right]], colWidths=[10*cm, 7.4*cm])
    header_outer.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)]))
    elements.append(header_outer)
    elements.append(Spacer(1, 0.4*cm))
    elements.append(HRFlowable(width="100%", thickness=2, color=PINK_MID, spaceAfter=0.3*cm))

    info_left  = Table([[Paragraph("TAGIHAN KEPADA", label_style)],[Paragraph(data['pembeli'], value_style)],[Paragraph("Pelanggan Zee Zee Dessert", tagline_style)]], colWidths=[8*cm])
    info_right = Table([
        [Paragraph("TANGGAL", label_style), Paragraph("NO. INVOICE", label_style)],
        [Paragraph(datetime.now().strftime('%d %B %Y'), value_style), Paragraph(data['invoice_no'], value_style)],
        [Paragraph("STATUS", label_style), Paragraph("JATUH TEMPO", label_style)],
        [Paragraph("LUNAS", ParagraphStyle('s', fontSize=10, fontName='Helvetica-Bold', textColor=colors.HexColor('#2E7D32'))), Paragraph(datetime.now().strftime('%d %B %Y'), value_style)]
    ], colWidths=[4.7*cm, 4.7*cm])
    info_left.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),PINK_PALE),('PADDING',(0,0),(-1,-1),8),('VALIGN',(0,0),(-1,-1),'TOP')]))
    info_right.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),GREY_LIGHT),('PADDING',(0,0),(-1,-1),8),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEAFTER',(0,0),(0,-1),0.5,colors.HexColor('#E0E0E0'))]))
    info_outer = Table([[info_left, info_right]], colWidths=[8*cm, 9.4*cm])
    info_outer.setStyle(TableStyle([('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0),('VALIGN',(0,0),(-1,-1),'TOP')]))
    elements.append(info_outer)
    elements.append(Spacer(1, 0.5*cm))

    table_data = [[Paragraph("NO",th_style),Paragraph("NAMA ITEM",th_style),Paragraph("QTY",th_style),Paragraph("HARGA SATUAN",th_style),Paragraph("SUBTOTAL",th_style)]]
    subtotal_all = 0
    for i, item in enumerate(data['items']):
        sub = item['qty'] * item['harga']
        subtotal_all += sub
        table_data.append([Paragraph(str(i+1),td_center),Paragraph(item['nama'],td_style),Paragraph(str(item['qty']),td_center),Paragraph(f"Rp {item['harga']:,}".replace(',','.'),td_right),Paragraph(f"Rp {sub:,}".replace(',','.'),td_right)])
    item_table = Table(table_data, colWidths=[1.2*cm,7*cm,2*cm,4.1*cm,3.1*cm], repeatRows=1)
    item_table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PINK_MID),('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE,GREY_LIGHT]),('ALIGN',(0,0),(0,-1),'CENTER'),('ALIGN',(2,0),(2,-1),'CENTER'),('ALIGN',(3,0),(4,-1),'RIGHT'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('LINEBELOW',(0,1),(-1,-1),0.3,colors.HexColor('#F0F0F0')),('BOX',(0,0),(-1,-1),0.5,colors.HexColor('#E0E0E0'))]))
    elements.append(item_table)
    elements.append(Spacer(1, 0.3*cm))

    ongkir = data.get('ongkir', 0)
    grand_total = subtotal_all + ongkir
    totals_data = [
        [Paragraph("Subtotal", sub_label), Paragraph(f"Rp {subtotal_all:,}".replace(',','.'), sub_value)],
        [Paragraph("Ongkos Kirim", sub_label), Paragraph(f"Rp {ongkir:,}".replace(',','.'), sub_value)],
        [Paragraph("TOTAL", tot_label), Paragraph(f"Rp {grand_total:,}".replace(',','.'), tot_value)]
    ]
    totals_table = Table(totals_data, colWidths=[8*cm, 4*cm])
    totals_table.setStyle(TableStyle([('ALIGN',(0,0),(-1,-1),'RIGHT'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),('LINEABOVE',(0,2),(-1,2),1,PINK_MID),('BACKGROUND',(0,2),(-1,2),PINK_DARK)]))
    outer_totals = Table([['', totals_table]], colWidths=[5.4*cm, 12*cm])
    outer_totals.setStyle(TableStyle([('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('VALIGN',(0,0),(-1,-1),'TOP')]))
    elements.append(outer_totals)
    elements.append(Spacer(1, 0.6*cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=PINK_LIGHT, spaceAfter=0.3*cm))

    footer_data = [[Paragraph("Terima kasih sudah memesan!\nSemoga harimu semanis dessert kami", footer_left), Paragraph("Zee Zee Dessert\nzeezeedessert@gmail.com", footer_right)]]
    footer_table = Table(footer_data, colWidths=[9*cm, 8.4*cm])
    footer_table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0)]))
    elements.append(footer_table)
    elements.append(Paragraph("Invoice ini dibuat otomatis oleh sistem Bot Zee Zee Dessert", note_style))
    doc.build(elements)
    return filename
