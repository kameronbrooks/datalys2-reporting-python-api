
import pandas as pd
import datetime
import numpy as np
from dl2_reports import DL2Report, aggregates as A, filters as F

def simple_kpi_report():
    report = DL2Report("Simple KPI Report", "A test report with a simple KPI", author="Test Bot")
    
    df = pd.DataFrame({
        "Category": ["A", "B", "C"],
        "Value": [100, 200, 300],
        "Goal": [90, 210, 290]
    })
    
    report.add_df("kpi_data", df)
    
    page = report.add_page("Dashboard")
    row = page.add_row()
    
    row.add_kpi(
        dataset_id="kpi_data",
        value_column="Value",
        title="Revenue",
        comparison_column="Goal",
        row_index=0
    )
    
    return report

def date_types_report():
    report = DL2Report("Date Types Report", compress_visuals=False)
    
    df = pd.DataFrame({
        "Date": [datetime.date(2023, 1, 1), datetime.date(2023, 1, 2)],
        "DateTime": [datetime.datetime(2023, 1, 1, 10, 0, 0), datetime.datetime(2023, 1, 2, 11, 30, 0)],
        "Value": [1.5, 2.5],
        "Nulls": [None, 3.0]
    })
    
    report.add_df("dates", df)
    
    page = report.add_page("Dates")
    row = page.add_row()
    
    row.add_visual("table", dataset_id="dates")
    
    return report

def complex_layout_report():
    report = DL2Report("Complex Layout")
    
    df = pd.DataFrame({"A": [1], "B": [2]})
    report.add_df("data", df)
    
    page = report.add_page("Main")
    
    r1 = page.add_row()
    r1.add_visual("text", title="Left")
    r1.add_visual("text", title="Right")
    
    return report

def table_report():
    report = DL2Report("Table Report")
    df = pd.DataFrame({
        "Name": ["Alice", "Bob", "Charlie"],
        "Age": [25, 30, 35],
        "City": ["NY", "LA", "SF"]
    })
    report.add_df("users", df)
    page = report.add_page("Table")
    page.add_row().add_table(
        dataset_id="users",
        columns=["Name", "City"],
        sort_column="Age",
        page_size=5
    )
    return report

def card_report():
    report = DL2Report("Card Report")
    page = report.add_page("Card")
    row = page.add_row()
    row.add_card(title="Welcome", text="This is a simple card.", content_type="text")
    row.add_card(title="HTML Card", text="<b>Bold Text</b>", content_type="html")
    return report

def pie_report():
    report = DL2Report("Pie Report")
    df = pd.DataFrame({
        "Segment": ["Direct", "Social", "Organic"],
        "Visits": [500, 300, 200]
    })
    report.add_df("traffic", df)
    page = report.add_page("Pie")
    row = page.add_row()
    row.add_pie(dataset_id="traffic", category_column="Segment", value_column="Visits", title="Traffic Source")
    row.add_pie(dataset_id="traffic", category_column="Segment", value_column="Visits", inner_radius=50, title="Donut")
    return report

def bar_report():
    report = DL2Report("Bar Report")
    df = pd.DataFrame({
        "Month": ["Jan", "Feb", "Mar"],
        "Sales": [100, 150, 200],
        "Cost": [80, 100, 120]
    })
    report.add_df("finance", df)
    page = report.add_page("Bar")
    row = page.add_row()
    # Clustered
    row.add_bar(dataset_id="finance", x_column="Month", y_columns=["Sales", "Cost"], title="Clustered")
    # Stacked
    row.add_bar(dataset_id="finance", x_column="Month", y_columns=["Sales", "Cost"], stacked=True, title="Stacked")
    return report

def scatter_report():
    report = DL2Report("Scatter Report")
    df = pd.DataFrame({
        "Height": [160, 170, 180, 165],
        "Weight": [60, 70, 80, 65],
        "Gender": ["F", "M", "M", "F"]
    })
    report.add_df("biometrics", df)
    page = report.add_page("Scatter")
    page.add_row().add_scatter(
        dataset_id="biometrics", 
        x_column="Height", 
        y_column="Weight", 
        category_column="Gender",
        show_trendline=True
    )
    return report

def line_report():
    report = DL2Report("Line Report")
    df = pd.DataFrame({
        "Day": [1, 2, 3, 4, 5],
        "Temperature": [20, 22, 21, 24, 25],
        "Humidity": [40, 45, 42, 38, 35]
    })
    report.add_df("weather", df)
    page = report.add_page("Line")
    page.add_row().add_line(
        dataset_id="weather", 
        x_column="Day", 
        y_columns=["Temperature", "Humidity"], 
        smooth=True
    )
    return report

def checklist_report():
    report = DL2Report("Checklist Report")
    df = pd.DataFrame({
        "Task": ["Task A", "Task B", "Task C"],
        "Completed": [True, False, False],
        "Due": pd.to_datetime(["2024-01-01", "2024-02-01", "2024-01-15"])
    })
    report.add_df("tasks", df)
    page = report.add_page("Checklist")
    page.add_row().add_checklist(
        dataset_id="tasks",
        status_column="Completed",
        warning_column="Due",
        warning_threshold=5,
        columns=["Task", "Due"],
        # dl2 0.4.1 table parity + checklist UX
        id="task-checklist",
        default_sort=[{"column": "status", "direction": "asc"}],
        max_height=400,
        hide_completed=True,
        column_formats={"Due": "date"},
        conditional_formats=[
            {"when": F.eq("Task", "Task B"), "style": "warning"},
        ],
    )
    return report

def histogram_report():
    report = DL2Report("Histogram Report")
    df = pd.DataFrame({
        "Age": np.random.normal(loc=30, scale=5, size=100) # Deterministic because we will control seed? 
                                                            # Actually, scenarios run inside patch, but numpy random isn't patched.
                                                            # I should use fixed data for stable tests.
    })
    # Replace random with fixed data
    df = pd.DataFrame({"Age": [20, 21, 22, 25, 25, 30, 30, 30, 35, 40, 45, 50]})
    
    report.add_df("population", df)
    page = report.add_page("Histogram")
    page.add_row().add_histogram(dataset_id="population", column="Age", bins=5)
    return report

def heatmap_report():
    report = DL2Report("Heatmap Report")
    df = pd.DataFrame({
        "X": ["A", "A", "B", "B"],
        "Y": ["1", "2", "1", "2"],
        "Val": [10, 20, 30, 40]
    })
    report.add_df("matrix", df)
    page = report.add_page("Heatmap")
    page.add_row().add_heatmap(dataset_id="matrix", x_column="X", y_column="Y", value_column="Val")
    return report

def boxplot_report():
    report = DL2Report("Boxplot Report")
    df = pd.DataFrame({
        "Group": ["A"]*5 + ["B"]*5,
        "Score": [1, 2, 5, 8, 9, 2, 3, 4, 5, 6]
    })
    report.add_df("scores", df)
    page = report.add_page("Boxplot")
    
    r = page.add_row()
    # Data mode
    r.add_boxplot(dataset_id="scores", data_column="Score", category_column="Group", title="From Data")
    
    # Pre-calc mode
    df_calc = pd.DataFrame({
        "Group": ["C"],
        "Min": [10], "Q1": [20], "Median": [30], "Q3": [40], "Max": [50]
    })
    report.add_df("calc", df_calc)
    
    r.add_boxplot(
        dataset_id="calc", 
        min_column="Min", q1_column="Q1", median_column="Median", q3_column="Q3", max_column="Max",
        title="Pre-calculated"
    )
    return report

def gauge_report():
    report = DL2Report("Gauge Report")
    df = pd.DataFrame({
        "Metric": ["Speed"],
        "Value": [80],
        "Min": [0],
        "Max": [120]
    })
    report.add_df("sensors", df)
    page = report.add_page("Gauge")
    page.add_row().add_gauge(dataset_id="sensors", value_column="Value", value_min=0, value_max=120, title="Speedometer")
    return report

def tabs_report():
    report = DL2Report("Tabs Report")
    df = pd.DataFrame({
        "Month": ["Jan", "Feb", "Mar"],
        "Revenue": [100, 150, 200]
    })
    report.add_df("sales", df)
    page = report.add_page("Tabs")
    row = page.add_row()

    tabs = row.add_tabs(id="sales-tabs", default_tab=0, title="Sales Views")
    tabs.add_tab("Chart").add_line(dataset_id="sales", x_column="Month", y_columns=["Revenue"])
    tabs.add_tab("Data", direction="column").add_table(dataset_id="sales", id="sales-table")
    tabs.add_tab("About").add_card(title="Info", text="Monthly revenue.", content_type="text")

    row.add_link(target_id="sales-table", label="Jump to data", link_style="button")
    return report


def filters_report():
    report = DL2Report("Filters Report")
    df = pd.DataFrame({
        "Region": ["North", "South", "North", "West"],
        "Category": ["A", "B", "A", "B"],
        "Amount": [100, 200, 300, 400]
    })
    report.add_df("sales", df)

    # Derived dataset: filtered + aggregated in the browser at load time
    report.add_derived_dataset(
        "north_by_category",
        "sales",
        filter=F.eq("Region", "North"),
        aggregate=A.aggregate("Category", A.agg("Amount", "sum", as_="Total")),
    )

    page = report.add_page("Filtered")
    row = page.add_row()

    # Per-visual filter: same shared dataset, different slice
    row.add_table(
        dataset_id="sales",
        title="Big Sales",
        filter=F.and_(F.gte("Amount", 200), F.isin("Region", ["South", "West"])),
    )

    # Per-visual aggregate
    row.add_bar(
        dataset_id="sales",
        x_column="Region",
        y_columns=["sum_Amount"],
        title="By Region",
        aggregate=A.aggregate("Region", A.agg("Amount", "sum")),
    )

    page.add_row().add_table(dataset_id="north_by_category", title="North by Category")
    return report


def table_features_report():
    report = DL2Report("Table Features Report", report_id="table-features")
    df = pd.DataFrame({
        "Region": ["North", "South", "East"],
        "Rep": ["Alice", "Bob", "Cara"],
        "Units": [10, 20, 30],
        "Amount": [100.0, 200.0, 300.0]
    })
    report.add_df("orders", df)

    modal = report.add_modal("order-detail", "Order Details")
    modal.add_row().add_card(
        title="Order — {{ row.Region }}",
        text="**Rep:** {{ row.Rep }}\n**Amount:** {{ formatCurrency(row.Amount) }}",
        content_type="md",
    )

    page = report.add_page("Orders")
    page.add_row().add_table(
        dataset_id="orders",
        id="orders-table",
        title="Orders",
        page_size=25,
        max_height=400,
        default_sort=[{"column": "Amount", "direction": "desc"}],
        hidden_columns=["Rep"],
        group_by="Region",
        group_aggregates=[A.agg("Amount", "sum")],
        total_row={"label": "Totals", "fns": {"Units": "sum", "Amount": "sum"}},
        total_column={"label": "Total", "columns": ["Units", "Amount"]},
        row_modal_id="order-detail",
        persist_state=True,
        export_file_name="orders.csv",
        # dl2 0.4.1 formatting
        column_formats={"Amount": {"format": "currency", "digits": 0}},
        conditional_formats=[
            {"when": F.gte("Amount", 300), "columns": ["Amount"], "style": "success"},
        ],
    )
    return report


scenarios = {
    "simple_kpi": simple_kpi_report,
    "date_types": date_types_report,
    "complex_layout": complex_layout_report,
    "table": table_report,
    "card": card_report,
    "pie": pie_report,
    "bar": bar_report,
    "scatter": scatter_report,
    "line": line_report,
    "checklist": checklist_report,
    "histogram": histogram_report,
    "heatmap": heatmap_report,
    "boxplot": boxplot_report,
    "gauge": gauge_report,
    "tabs": tabs_report,
    "filters": filters_report,
    "table_features": table_features_report
}
