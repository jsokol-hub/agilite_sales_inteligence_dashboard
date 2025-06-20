import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import glob
import re

# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def extract_category(title):
    """Extract main category from product title"""
    # Common categories in Hebrew
    categories = {
        'קרמון': 'Plate Carriers',
        'חגורת': 'Belts',
        'פאוץ': 'Pouches',
        'כפפות': 'Gloves',
        'כובע': 'Hats',
        'משקפי': 'Glasses',
        'פאנל': 'Panels',
        'פאץ': 'Patches',
        'שרוול': 'Sleeves',
        'ער"ד': 'Medical',
        'פלטה': 'Plates',
        'מערכת': 'Systems'
    }
    
    for heb, eng in categories.items():
        if heb in title:
            return eng
    return 'Other'

def load_latest_data():
    """Load the most recent processed data file"""
    processed_files = glob.glob(os.path.join("data", "processed", "processed_products_*.csv"))
    if not processed_files:
        return pd.DataFrame()
        
    latest_file = max(processed_files, key=os.path.getctime)
    df = pd.read_csv(latest_file)
    
    # Add category column
    df['category'] = df['title'].apply(extract_category)
    return df

def load_stock_history():
    """Загрузить историю остатков по всем processed-файлам"""
    processed_files = glob.glob(os.path.join("data", "processed", "processed_products_*.csv"))
    history = []
    for file in sorted(processed_files):
        date_str = re.search(r"processed_products_(\d{8}_\d{6})", file)
        if date_str:
            date = datetime.strptime(date_str.group(1), "%Y%m%d_%H%M%S")
        else:
            date = datetime.fromtimestamp(os.path.getctime(file))
        df = pd.read_csv(file)
        if 'stock_status' not in df.columns:
            continue
        in_stock = (df['stock_status'] == 'In Stock').sum()
        # По категориям
        if 'title' in df.columns:
            df['category'] = df['title'].apply(extract_category)
            cat_counts = df[df['stock_status'] == 'In Stock']['category'].value_counts().to_dict()
        else:
            cat_counts = {}
        history.append({
            'date': date,
            'in_stock': in_stock,
            'category_counts': cat_counts
        })
    return history

def load_variant_type_history():
    processed_files = glob.glob(os.path.join("data", "processed", "processed_products_*.csv"))
    history = []
    for file in sorted(processed_files):
        date_str = re.search(r"processed_products_(\d{8}_\d{6})", file)
        if date_str:
            date = datetime.strptime(date_str.group(1), "%Y%m%d_%H%M%S")
        else:
            date = datetime.fromtimestamp(os.path.getctime(file))
        df = pd.read_csv(file)
        if 'variant_types' not in df.columns:
            continue
        # Count products with each variant type (e.g., color, size)
        type_counts = {"color": 0, "size": 0}
        for types in df['variant_types'].fillna('[]'):
            try:
                types_list = eval(types) if isinstance(types, str) else types
                if "color" in types_list:
                    type_counts["color"] += 1
                if "size" in types_list:
                    type_counts["size"] += 1
            except Exception:
                continue
        history.append({
            'date': date,
            'color': type_counts["color"],
            'size': type_counts["size"]
        })
    return history

def create_variant_distribution_chart(df):
    """Create a pie chart showing variant distribution"""
    variant_counts = df['variant_count'].value_counts()
    fig = px.pie(
        values=variant_counts.values,
        names=[f'{x} variants' for x in variant_counts.index],
        title='Product Variant Distribution'
    )
    return fig

def create_price_distribution_chart(df):
    """Create a histogram of price distribution"""
    fig = px.histogram(
        df,
        x='price',
        title='Price Distribution',
        labels={'price': 'Price (₪)'},
        nbins=20
    )
    fig.update_layout(
        xaxis_title="Price (₪)",
        yaxis_title="Number of Products"
    )
    return fig

def create_category_distribution_chart(df):
    """Create a bar chart showing category distribution"""
    category_counts = df['category'].value_counts()
    fig = px.bar(
        x=category_counts.index,
        y=category_counts.values,
        title='Product Category Distribution',
        labels={'x': 'Category', 'y': 'Number of Products'}
    )
    fig.update_layout(
        xaxis_title="Category",
        yaxis_title="Number of Products",
        xaxis_tickangle=45
    )
    return fig

def create_stock_status_chart(df):
    """Create a pie chart showing stock status distribution"""
    stock_counts = df['stock_status'].value_counts()
    fig = px.pie(
        values=stock_counts.values,
        names=stock_counts.index,
        title='Product Stock Status Distribution'
    )
    return fig

def create_top_products_table(df):
    """Create a table of top products by price with links"""
    top_products = df.sort_values('price', ascending=False).head(10)
    
    # Create table with links
    table_data = []
    for _, row in top_products.iterrows():
        table_data.append({
            'Title': html.A(row['title'], href=row['url'], target='_blank'),
            'Price': f"₪{row['price']:.2f}",
            'Category': row['category'],
            'Stock Status': row['stock_status'] if pd.notna(row['stock_status']) else 'Unknown',
            'Variants': row['variant_count'],
            'Images': row['image_count']
        })
    
    return dbc.Table.from_dataframe(
        pd.DataFrame(table_data),
        striped=True,
        bordered=True,
        hover=True
    )

def create_stock_history_chart(history):
    """График динамики общего количества товаров в наличии"""
    if not history:
        fig = go.Figure()
        fig.add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    dates = [h['date'] for h in history]
    in_stock = [h['in_stock'] for h in history]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=in_stock, mode='lines+markers', name='In Stock'))
    fig.update_layout(title="Stock Level Over Time", xaxis_title="Date", yaxis_title="Number of Products In Stock")
    return fig

def create_category_stock_history_chart(history):
    """График динамики остатков по категориям"""
    if not history or not any(h['category_counts'] for h in history):
        fig = go.Figure()
        fig.add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    dates = [h['date'] for h in history]
    # Соберём все категории
    all_cats = set()
    for h in history:
        all_cats.update(h['category_counts'].keys())
    fig = go.Figure()
    for cat in sorted(all_cats):
        y = [h['category_counts'].get(cat, 0) for h in history]
        fig.add_trace(go.Scatter(x=dates, y=y, mode='lines+markers', name=cat))
    fig.update_layout(title="Stock Level by Category Over Time", xaxis_title="Date", yaxis_title="Number of Products In Stock")
    return fig

def create_variant_type_history_chart(history):
    if not history:
        fig = go.Figure()
        fig.add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    dates = [h['date'] for h in history]
    color_counts = [h['color'] for h in history]
    size_counts = [h['size'] for h in history]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=color_counts, mode='lines+markers', name='Color Variants'))
    fig.add_trace(go.Scatter(x=dates, y=size_counts, mode='lines+markers', name='Size Variants'))
    fig.update_layout(title="Variant Type Dynamics Over Time", xaxis_title="Date", yaxis_title="Number of Products")
    return fig

# Define the layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Agilite Sales Intelligence Dashboard", className="text-center my-4"), width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            html.H3("Category Distribution"),
            dcc.Graph(id='category-distribution-chart')
        ], width=6),
        
        dbc.Col([
            html.H3("Stock Status Distribution"),
            dcc.Graph(id='stock-status-chart')
        ], width=6)
    ]),
    
    dbc.Row([
        dbc.Col([
            html.H3("Variant Distribution"),
            dcc.Graph(id='variant-distribution-chart')
        ], width=6),
        
        dbc.Col([
            html.H3("Price Distribution"),
            dcc.Graph(id='price-distribution-chart')
        ], width=6)
    ]),
    
    dbc.Row([
        dbc.Col([
            html.H3("Top Products by Price"),
            html.Div(id='top-products-table')
        ], width=12)
    ]),

    dbc.Row([
        dbc.Col([
            html.H3("Stock Level Over Time"),
            dcc.Graph(id='stock-history-chart')
        ], width=6),
        dbc.Col([
            html.H3("Stock by Category Over Time"),
            dcc.Graph(id='category-stock-history-chart')
        ], width=6)
    ]),
    
    dbc.Row([
        dbc.Col([
            html.H3("Variant Type Dynamics Over Time"),
            dcc.Graph(id='variant-type-history-chart')
        ], width=12)
    ]),
    
    dcc.Interval(
        id='interval-component',
        interval=5*60*1000,  # Update every 5 minutes
        n_intervals=0
    )
])

@app.callback(
    [Output('variant-distribution-chart', 'figure'),
     Output('price-distribution-chart', 'figure'),
     Output('category-distribution-chart', 'figure'),
     Output('stock-status-chart', 'figure'),
     Output('top-products-table', 'children'),
     Output('stock-history-chart', 'figure'),
     Output('category-stock-history-chart', 'figure'),
     Output('variant-type-history-chart', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    df = load_latest_data()
    history = load_stock_history()
    variant_type_history = load_variant_type_history()
    
    # Create empty figures for when data is not available
    empty_fig = go.Figure()
    empty_fig.add_annotation(
        text="No data available",
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False
    )
    
    if df.empty:
        return empty_fig, empty_fig, empty_fig, empty_fig, "No data available", empty_fig, empty_fig, empty_fig
    
    try:
        variant_chart = create_variant_distribution_chart(df)
        price_chart = create_price_distribution_chart(df)
        category_chart = create_category_distribution_chart(df)
        stock_chart = create_stock_status_chart(df)
        top_products = create_top_products_table(df)
        stock_history_chart = create_stock_history_chart(history)
        category_stock_history_chart = create_category_stock_history_chart(history)
        variant_type_history_chart = create_variant_type_history_chart(variant_type_history)
        
        return variant_chart, price_chart, category_chart, stock_chart, top_products, stock_history_chart, category_stock_history_chart, variant_type_history_chart
    except Exception as e:
        print(f"Error updating dashboard: {str(e)}")
        return empty_fig, empty_fig, empty_fig, empty_fig, f"Error updating dashboard: {str(e)}", empty_fig, empty_fig, empty_fig

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050) 