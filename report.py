from database import get_connection
from fpdf import FPDF
from datetime import datetime
import os

REPORT_DIR = r"C:\Users\Piyush Ranjan\generatedreport"
os.makedirs(REPORT_DIR, exist_ok=True)


def generate_user_report():
    """Generate a PDF report with all user details (same as display_users)."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id, name, dl_no, email, phone, address FROM users")
    users = cursor.fetchall()

    if not users:
        print("No users found.")
        cursor.close()
        conn.close()
        return

    pdf = FPDF(orientation="L")  # Landscape for wider table
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ---- Title ----
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "RentXDrive - User Report", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Generated on: {datetime.now().strftime('%d-%m-%Y  %I:%M %p')}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(8)

    # ---- Table Header ----
    col_widths = [20, 35, 30, 55, 30, 40, 25, 22, 20]
    headers = ["User ID", "Name", "DL No", "Email", "Phone", "Address",
               "Bookings", "Revenue", "Rejected"]

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(50, 50, 80)
    pdf.set_text_color(255, 255, 255)

    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, border=1, align="C", fill=True)
    pdf.ln()

    # ---- Table Rows ----
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(0, 0, 0)
    fill = False

    for u in users:
        uid, name, dl_no, email, phone, address = u

        # Confirmed bookings
        cursor.execute("""
            SELECT COUNT(*) FROM bookings WHERE user_id=%s AND status='Booked'
        """, (uid,))
        active_bookings = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM user_history WHERE user_id=%s AND status='Completed'
        """, (uid,))
        completed_bookings = cursor.fetchone()[0]

        total_confirmed = active_bookings + completed_bookings

        # Total revenue
        cursor.execute("""
            SELECT COALESCE(SUM(total_amount), 0) FROM bookings WHERE user_id=%s AND status='Booked'
        """, (uid,))
        active_revenue = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COALESCE(SUM(total_amount), 0) FROM user_history WHERE user_id=%s AND status='Completed'
        """, (uid,))
        completed_revenue = cursor.fetchone()[0]

        total_revenue = active_revenue + completed_revenue

        # Rejection count
        cursor.execute("""
            SELECT COUNT(*) FROM user_history WHERE user_id=%s AND status='Rejected'
        """, (uid,))
        rejection_count = cursor.fetchone()[0]

        confirmed_str = str(total_confirmed) if total_confirmed > 0 else "No bookings"
        revenue_str = f"Rs.{total_revenue}" if total_confirmed > 0 else "N/A"
        rejected_str = str(rejection_count) if rejection_count > 0 else "No rejections"

        row = [str(uid), str(name), str(dl_no), str(email), str(phone), str(address),
               confirmed_str, revenue_str, rejected_str]

        if fill:
            pdf.set_fill_color(230, 230, 240)
        else:
            pdf.set_fill_color(255, 255, 255)

        row_height = 8

        # Check page break
        if pdf.get_y() + row_height > pdf.h - 15:
            pdf.add_page()

        for i, val in enumerate(row):
            pdf.cell(col_widths[i], row_height, val, border=1, align="C", fill=True)
        pdf.ln()

        fill = not fill

    cursor.close()
    conn.close()

    # Save file
    filename = f"User_Report_{datetime.now().strftime('%d%m%Y_%H%M%S')}.pdf"
    filepath = os.path.join(REPORT_DIR, filename)
    pdf.output(filepath)
    print(f"\nReport generated successfully: {filepath}")


def generate_vehicle_report():
    """Generate a PDF report with all vehicle usage details (same as view_vehicle_usage)."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT vehicle_id, type, model FROM vehicles")
    vehicles = cursor.fetchall()

    if not vehicles:
        print("No vehicles found.")
        cursor.close()
        conn.close()
        return

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ---- Title ----
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "RentXDrive - Vehicle Report", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Generated on: {datetime.now().strftime('%d-%m-%Y  %I:%M %p')}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(8)

    # ---- Table Header ----
    col_widths = [30, 30, 40, 35, 35, 25]
    headers = ["Vehicle ID", "Type", "Model", "Total Bookings", "Total Revenue", "Avg Rating"]

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(50, 50, 80)
    pdf.set_text_color(255, 255, 255)

    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, border=1, align="C", fill=True)
    pdf.ln()

    # ---- Table Rows ----
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(0, 0, 0)
    fill = False

    for v in vehicles:
        vid, vtype, model = v

        # Total confirmed bookings
        cursor.execute("""
            SELECT COUNT(*) FROM bookings WHERE vehicle_id=%s AND status='Booked'
        """, (vid,))
        active_bookings = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM user_history WHERE vehicle_id=%s AND status='Completed'
        """, (vid,))
        completed_bookings = cursor.fetchone()[0]

        total_bookings = active_bookings + completed_bookings

        # Total revenue
        cursor.execute("""
            SELECT COALESCE(SUM(total_amount), 0) FROM bookings WHERE vehicle_id=%s AND status='Booked'
        """, (vid,))
        active_revenue = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COALESCE(SUM(total_amount), 0) FROM user_history WHERE vehicle_id=%s AND status='Completed'
        """, (vid,))
        completed_revenue = cursor.fetchone()[0]

        total_revenue = active_revenue + completed_revenue

        # Average rating
        cursor.execute("""
            SELECT AVG(rating) FROM user_history
            WHERE vehicle_id=%s AND rating IS NOT NULL
        """, (vid,))
        avg_rating = cursor.fetchone()[0]

        rating_str = str(round(avg_rating, 1)) if avg_rating is not None else "No Ratings"

        row = [str(vid), str(vtype), str(model), str(total_bookings),
               f"Rs.{total_revenue}", rating_str]

        if fill:
            pdf.set_fill_color(230, 230, 240)
        else:
            pdf.set_fill_color(255, 255, 255)

        row_height = 9

        if pdf.get_y() + row_height > pdf.h - 15:
            pdf.add_page()

        for i, val in enumerate(row):
            pdf.cell(col_widths[i], row_height, val, border=1, align="C", fill=True)
        pdf.ln()

        fill = not fill

    cursor.close()
    conn.close()

    filename = f"Vehicle_Report_{datetime.now().strftime('%d%m%Y_%H%M%S')}.pdf"
    filepath = os.path.join(REPORT_DIR, filename)
    pdf.output(filepath)
    print(f"\nReport generated successfully: {filepath}")


def generate_report():
    """Main menu for report generation."""

    print("\n--- GENERATE REPORT ---")
    print("1. Users Report")
    print("2. Vehicle Report")
    print("3. Back")

    choice = input("Enter choice: ")

    match choice:
        case "1":
            generate_user_report()
        case "2":
            generate_vehicle_report()
        case "3":
            return
        case _:
            print("Invalid Choice")