from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import numpy as np
from datetime import datetime


def generate_detailed_report(results, filename="results/T4_simulation_report.pdf"):
    """Generate detailed PDF report with simulation statistics"""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = ParagraphStyle(
        "CustomTitle", parent=styles["Heading1"], fontSize=16, spaceAfter=30
    )
    elements.append(Paragraph("Madrid T4 Airport Simulation Report", title_style))
    elements.append(
        Paragraph(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]
        )
    )
    elements.append(Spacer(1, 20))

    # Overall Statistics
    elements.append(Paragraph("Overall Statistics", styles["Heading2"]))
    overall_data = [
        ["Total Passengers", str(results["total_passengers"])],
        ["Processed Passengers", str(results["processed_passengers"])],
        ["Average Total Time", f"{results['avg_total_time']:.1f} minutes"],
        ["Maximum Total Time", f"{results['max_total_time']:.1f} minutes"],
    ]
    overall_table = Table(overall_data)
    overall_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )
    elements.append(overall_table)
    elements.append(Spacer(1, 20))

    # Station Statistics
    elements.append(Paragraph("Station Performance", styles["Heading2"]))

    stations = ["checkin", "security", "passport", "boarding"]
    station_data = [["Metric", "Check-in", "Security", "Passport", "Boarding"]]

    metrics = [
        ("Average Wait (min)", "_avg_wait"),
        ("Maximum Wait (min)", "_max_wait"),
        ("Average Queue Length", "_queue_length"),
        ("Maximum Queue", "_max_queue"),
    ]

    for metric_name, suffix in metrics:
        row = [metric_name]
        for station in stations:
            value = results.get(f"{station}{suffix}", 0)
            row.append(f"{value:.1f}")
        station_data.append(row)

    station_table = Table(station_data)
    station_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )
    elements.append(station_table)
    elements.append(Spacer(1, 20))

    # Utilization Analysis
    elements.append(Paragraph("Resource Utilization Analysis", styles["Heading2"]))
    util_data = [["Station", "Average", "Peak", "Minimum"]]

    for station in stations:
        util_values = results.get(f"{station}_utilization", [])
        if util_values:
            util_data.append(
                [
                    station.capitalize(),
                    f"{np.mean(util_values):.1%}",
                    f"{np.max(util_values):.1%}",
                    f"{np.min(util_values):.1%}",
                ]
            )

    util_table = Table(util_data)
    util_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )
    elements.append(util_table)

    # Build PDF
    doc.build(elements)
