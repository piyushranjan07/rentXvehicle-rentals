from database import get_connection
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from datetime import datetime


# ── colour palette ────
BG        = "#0f1117"
PANEL     = "#1a1d2e"
ACCENT1   = "#7c3aed"   # violet
ACCENT2   = "#06b6d4"   # cyan
ACCENT3   = "#f59e0b"   # amber
GRID      = "#2a2d3e"
TEXT      = "#e2e8f0"
SUBTEXT   = "#94a3b8"


def _apply_dark_style(fig, ax, title):
    """Apply a premium dark theme to any axes."""
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(PANEL)

    ax.set_title(title, color=TEXT, fontsize=14, fontweight="bold", pad=14)
    ax.tick_params(colors=SUBTEXT, labelsize=9)
    ax.xaxis.label.set_color(SUBTEXT)
    ax.yaxis.label.set_color(SUBTEXT)

    for spine in ax.spines.values():
        spine.set_edgecolor(GRID)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda x, _: f"₹{int(x):,}"
    ))
    ax.grid(axis="y", color=GRID, linewidth=0.8, linestyle="--")
    ax.set_axisbelow(True)


# ── 1. Revenue by Day ─────────
def revenue_by_day():
    print("\n--- Filter Revenue by Day ---")
    print("Format exactly as YYYY-MM-DD (e.g., 2024-05-15)")
    start_date = input("Enter Start Date [Press Enter for all]: ").strip()
    end_date   = input("Enter End Date [Press Enter for all]: ").strip()

    conn = get_connection()
    if not conn:
        print("Database connection failed.")
        return
    cursor = conn.cursor()

    query_b = """
        SELECT DATE(confirmation_time), COALESCE(SUM(total_amount), 0)
        FROM bookings
        WHERE status = 'Booked' AND confirmation_time IS NOT NULL
    """
    query_h = """
        SELECT DATE(confirmation_time), COALESCE(SUM(total_amount), 0)
        FROM user_history
        WHERE status = 'Completed' AND confirmation_time IS NOT NULL
    """
    
    params = []
    if start_date:
        query_b += " AND DATE(confirmation_time) >= %s"
        query_h += " AND DATE(confirmation_time) >= %s"
        params.append(start_date)
    if end_date:
        query_b += " AND DATE(confirmation_time) <= %s"
        query_h += " AND DATE(confirmation_time) <= %s"
        params.append(end_date)

    query_b += " GROUP BY DATE(confirmation_time) ORDER BY DATE(confirmation_time)"
    query_h += " GROUP BY DATE(confirmation_time) ORDER BY DATE(confirmation_time)"

    cursor.execute(query_b, tuple(params))
    active = cursor.fetchall()

    cursor.execute(query_h, tuple(params))
    history = cursor.fetchall()

    cursor.close()
    conn.close()

    revenue_map = {}
    for date, amt in active + history:
        revenue_map[date] = revenue_map.get(date, 0) + float(amt)

    if not revenue_map:
        print("No revenue data found for this date range.")
        return

    dates  = sorted(revenue_map.keys())
    values = [revenue_map[d] for d in dates]
    labels = [d.strftime("%d %b %Y") if hasattr(d, "strftime") else str(d) for d in dates]

    fig, ax = plt.subplots(figsize=(13, 5))

    # Line graph with filled area
    ax.fill_between(labels, values, alpha=0.25, color=ACCENT1)
    ax.plot(labels, values, color=ACCENT1, linewidth=2.5, marker="o",
            markersize=7, markerfacecolor=ACCENT1, zorder=4)

    for x, val in enumerate(values):
        ax.text(x, val + max(values) * 0.015, f"₹{int(val):,}",
                ha="center", va="bottom", color=TEXT, fontsize=7.5)

    ax.set_xlabel("Confirmation Date", labelpad=8)
    ax.set_ylabel("Revenue (₹)", labelpad=8)
    plt.xticks(rotation=45, ha="right")
    _apply_dark_style(fig, ax, "Revenue by Day")
    plt.tight_layout()
    plt.show()


# ── 2. Revenue by Month ───────
def revenue_by_month():
    print("\n--- Filter Revenue by Month ---")
    print("Format exactly as YYYY-MM (e.g., 2024-05)")
    start_month = input("Enter Start Month & Year [Press Enter for all]: ").strip()
    end_month   = input("Enter End Month & Year [Press Enter for all]: ").strip()

    conn = get_connection()
    if not conn:
        print("Database connection failed.")
        return
    cursor = conn.cursor()

    query_b = """
        SELECT DATE_FORMAT(confirmation_time, '%Y-%m'), COALESCE(SUM(total_amount), 0)
        FROM bookings
        WHERE status = 'Booked' AND confirmation_time IS NOT NULL
    """
    query_h = """
        SELECT DATE_FORMAT(confirmation_time, '%Y-%m'), COALESCE(SUM(total_amount), 0)
        FROM user_history
        WHERE status = 'Completed' AND confirmation_time IS NOT NULL
    """

    params = []
    if start_month:
        query_b += " AND DATE_FORMAT(confirmation_time, '%Y-%m') >= %s"
        query_h += " AND DATE_FORMAT(confirmation_time, '%Y-%m') >= %s"
        params.append(start_month)
    if end_month:
        query_b += " AND DATE_FORMAT(confirmation_time, '%Y-%m') <= %s"
        query_h += " AND DATE_FORMAT(confirmation_time, '%Y-%m') <= %s"
        params.append(end_month)

    query_b += " GROUP BY DATE_FORMAT(confirmation_time, '%Y-%m') ORDER BY DATE_FORMAT(confirmation_time, '%Y-%m')"
    query_h += " GROUP BY DATE_FORMAT(confirmation_time, '%Y-%m') ORDER BY DATE_FORMAT(confirmation_time, '%Y-%m')"

    cursor.execute(query_b, tuple(params))
    active = cursor.fetchall()

    cursor.execute(query_h, tuple(params))
    history = cursor.fetchall()

    cursor.close()
    conn.close()

    revenue_map = {}
    for period, amt in active + history:
        revenue_map[period] = revenue_map.get(period, 0) + float(amt)

    if not revenue_map:
        print("No revenue data found for this month range.")
        return

    periods  = sorted(revenue_map.keys())
    values   = [revenue_map[p] for p in periods]
    labels   = [datetime.strptime(p, "%Y-%m").strftime("%b %Y") for p in periods]

    fig, ax = plt.subplots(figsize=(12, 5))

    # Bar chart
    bars = ax.bar(labels, values, color=ACCENT2, width=0.6, zorder=3)

    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(values) * 0.01,
            f"₹{int(val):,}",
            ha="center", va="bottom", color=TEXT, fontsize=8
        )

    ax.set_xlabel("Month of Confirmation", labelpad=8)
    ax.set_ylabel("Revenue (₹)", labelpad=8)
    plt.xticks(rotation=30, ha="right")
    _apply_dark_style(fig, ax, "Revenue by Month")
    plt.tight_layout()
    plt.show()


# ── 3. Vehicle-wise Revenue ──────
def vehicle_wise_revenue():
    print("\n--- Filter Vehicle-wise Revenue ---")
    start_date = input("Enter Start Date (YYYY-MM-DD) or Month (YYYY-MM) [Press Enter for all]: ").strip()
    end_date   = input("Enter End Date (YYYY-MM-DD) or Month (YYYY-MM) [Press Enter for all]: ").strip()

    conn = get_connection()
    if not conn:
        print("Database connection failed.")
        return
    cursor = conn.cursor()

    cursor.execute("SELECT vehicle_id, type, model FROM vehicles")
    vehicles = cursor.fetchall()

    if not vehicles:
        print("No vehicles found.")
        cursor.close()
        conn.close()
        return

    labels, totals = [], []

    for vid, vtype, model in vehicles:
        query_b = "SELECT COALESCE(SUM(total_amount), 0) FROM bookings WHERE vehicle_id=%s AND status='Booked' AND confirmation_time IS NOT NULL"
        query_h = "SELECT COALESCE(SUM(total_amount), 0) FROM user_history WHERE vehicle_id=%s AND status='Completed' AND confirmation_time IS NOT NULL"
        
        params = [vid]
        
        # Determine the correct format for the date condition
        if start_date:
            col_format = "DATE_FORMAT(confirmation_time, '%Y-%m')" if len(start_date) == 7 else "DATE(confirmation_time)"
            query_b += f" AND {col_format} >= %s"
            query_h += f" AND {col_format} >= %s"
            params.append(start_date)
            
        if end_date:
            col_format = "DATE_FORMAT(confirmation_time, '%Y-%m')" if len(end_date) == 7 else "DATE(confirmation_time)"
            query_b += f" AND {col_format} <= %s"
            query_h += f" AND {col_format} <= %s"
            params.append(end_date)

        cursor.execute(query_b, tuple(params))
        active_rev = float(cursor.fetchone()[0])

        cursor.execute(query_h, tuple(params))
        hist_rev = float(cursor.fetchone()[0])

        total = active_rev + hist_rev
        if total > 0:                          # skip zero-revenue vehicles
            labels.append(f"{model}\n({vtype})")
            totals.append(total)

    cursor.close()
    conn.close()

    if not labels:
        print("No vehicle revenue data found for this range.")
        return

    # Sort descending
    paired  = sorted(zip(totals, labels), reverse=True)
    totals  = [p[0] for p in paired]
    labels  = [p[1] for p in paired]

    # Colour gradient
    cmap   = plt.colormaps["cool"].resampled(len(labels))
    colors = [cmap(i) for i in range(len(labels))]

    fig, ax = plt.subplots(figsize=(max(10, len(labels) * 1.4), 6))
    bars = ax.bar(labels, totals, color=colors, width=0.6, zorder=3)

    for bar, val in zip(bars, totals):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(totals) * 0.01,
            f"₹{int(val):,}",
            ha="center", va="bottom", color=TEXT, fontsize=8
        )

    ax.set_xlabel("Vehicle (Type)", labelpad=8)
    ax.set_ylabel("Revenue (₹)", labelpad=8)
    _apply_dark_style(fig, ax, "Vehicle-wise Revenue")
    plt.tight_layout()
    plt.show()


# ── Menu ──────
def visualise_menu():
    while True:
        print("\n---- VISUALISE DATA ----")
        print("1. Revenue by Day")
        print("2. Revenue by Month")
        # print("3. Vehicle-wise Revenue")
        print("4. Back")

        choice = input("Enter choice: ").strip()

        match choice:
            case "1":
                revenue_by_day()
            case "2":
                revenue_by_month()
            # case "3":
            #     vehicle_wise_revenue()
            case "3":
                break
            case _:
                print("Invalid choice. Please enter 1-4.")
