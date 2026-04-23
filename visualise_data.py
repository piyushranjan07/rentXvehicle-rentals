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

    # ── fetch all distinct vehicle types ──
    cursor.execute("SELECT DISTINCT type FROM vehicles ORDER BY type")
    types = [row[0] for row in cursor.fetchall()]

    if not types:
        print("No vehicles found.")
        cursor.close()
        conn.close()
        return

    # ── build shared date condition (appended to every query) ──
    date_params = []
    date_cond   = ""
    if start_date:
        col_fmt   = "DATE_FORMAT(confirmation_time,'%Y-%m')" if len(start_date) == 7 else "DATE(confirmation_time)"
        date_cond += f" AND {col_fmt} >= %s"
        date_params.append(start_date)
    if end_date:
        col_fmt   = "DATE_FORMAT(confirmation_time,'%Y-%m')" if len(end_date) == 7 else "DATE(confirmation_time)"
        date_cond += f" AND {col_fmt} <= %s"
        date_params.append(end_date)

    # ── collect (vehicle_id, model, booking_count, total_revenue) per type ──
    type_data = {}   # { vtype: [(vid, model, bookings, revenue), ...] }

    cursor.execute("SELECT vehicle_id, type, model FROM vehicles ORDER BY type, vehicle_id")
    vehicles = cursor.fetchall()

    for vid, vtype, model in vehicles:
        p = [vid] + date_params

        cursor.execute(
            f"SELECT COUNT(*) FROM bookings "
            f"WHERE vehicle_id=%s AND status='Booked' AND confirmation_time IS NOT NULL{date_cond}",
            tuple(p)
        )
        cnt_b = cursor.fetchone()[0]

        cursor.execute(
            f"SELECT COUNT(*) FROM user_history "
            f"WHERE vehicle_id=%s AND status='Completed' AND confirmation_time IS NOT NULL{date_cond}",
            tuple(p)
        )
        cnt_h = cursor.fetchone()[0]

        cursor.execute(
            f"SELECT COALESCE(SUM(total_amount),0) FROM bookings "
            f"WHERE vehicle_id=%s AND status='Booked' AND confirmation_time IS NOT NULL{date_cond}",
            tuple(p)
        )
        rev_b = float(cursor.fetchone()[0])

        cursor.execute(
            f"SELECT COALESCE(SUM(total_amount),0) FROM user_history "
            f"WHERE vehicle_id=%s AND status='Completed' AND confirmation_time IS NOT NULL{date_cond}",
            tuple(p)
        )
        rev_h = float(cursor.fetchone()[0])

        bookings = cnt_b + cnt_h
        revenue  = rev_b + rev_h

        # include vehicle even if only bookings or only revenue is non-zero
        if bookings > 0 or revenue > 0:
            type_data.setdefault(vtype, []).append((vid, model, bookings, revenue))

    cursor.close()
    conn.close()

    active_types = [t for t in types if t in type_data]

    if not active_types:
        print("No vehicle data found for this range.")
        return

    # ── one FIGURE per vehicle type (all open simultaneously) ──
    type_cmaps = ["cool", "autumn", "summer", "winter", "spring", "plasma"]

    for t_idx, vtype in enumerate(active_types):
        # sort by number of bookings (descending)
        entries  = sorted(type_data[vtype], key=lambda x: x[2], reverse=True)
        x_labels = [f"ID:{e[0]}\n{e[1]}" for e in entries]
        bookings = [e[2] for e in entries]
        revenues = [e[3] for e in entries]

        cmap   = plt.colormaps[type_cmaps[t_idx % len(type_cmaps)]].resampled(max(len(x_labels), 2))
        colors = [cmap(i) for i in range(len(x_labels))]

        fig_w = max(10, len(x_labels) * 2.2)
        fig, ax = plt.subplots(figsize=(fig_w, 6))
        fig.patch.set_facecolor(BG)

        bars  = ax.bar(x_labels, bookings, color=colors, width=0.55, zorder=3)
        max_b = max(bookings) if max(bookings) > 0 else 1

        for bar, cnt, rev in zip(bars, bookings, revenues):
            bx  = bar.get_x() + bar.get_width() / 2
            bh  = bar.get_height()

            # ── booking count: just above the bar ──
            ax.text(bx, bh + max_b * 0.018,
                    str(cnt),
                    ha="center", va="bottom",
                    color=TEXT, fontsize=10, fontweight="bold")

            # ── total revenue: centred inside the bar rectangle ──
            if bh > 0:
                ax.text(bx, bh / 2,
                        f"₹{int(rev):,}",
                        ha="center", va="center",
                        color="white", fontsize=8, fontweight="bold",
                        rotation=90)

        ax.set_xlabel("Vehicle ID / Model", labelpad=8)
        ax.set_ylabel("Number of Bookings", labelpad=8)
        _apply_dark_style(fig, ax, f"{vtype}  —  No. of Bookings")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x)}"))
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
        plt.tight_layout()

    plt.show()      # open ALL figures at once


# ── Menu ──────
def visualise_menu():
    while True:
        print("\n---- VISUALISE DATA ----")
        print("1. Revenue by Day")
        print("2. Revenue by Month")
        print("3. Vehicle-wise Revenue")
        print("4. Back")

        choice = input("Enter choice: ").strip()

        match choice:
            case "1":
                revenue_by_day()
            case "2":
                revenue_by_month()
            case "3":
                vehicle_wise_revenue()
            case "4":
                break
            case _:
                print("Invalid choice. Please enter 1-4.")
