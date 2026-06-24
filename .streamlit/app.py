import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(
page_title="ЛМК по Северу",
page_icon="📊",
layout="wide"
)

st.title("📊 ЛМК по Северу")

uploaded_file = st.file_uploader(
"Загрузите Excel файл",
type=["xlsx"]
)

if uploaded_file is not None:

```
df = pd.read_excel(uploaded_file)

df.columns = [str(col).strip() for col in df.columns]

column_mapping = {}

for col in df.columns:
    col_lower = col.lower()

    if col_lower in ["сотрудник", "фио", "фио сотрудника", "работник"]:
        column_mapping["employee"] = col

    elif col_lower in ["город", "локация", "населенный пункт"]:
        column_mapping["city"] = col

    elif col_lower in ["руководитель", "начальник", "руководитель подразделения"]:
        column_mapping["manager"] = col

    elif "статус" in col_lower:
        column_mapping["status"] = col

required = ["employee", "city", "manager", "status"]

missing = [x for x in required if x not in column_mapping]

if missing:
    st.error(
        f"Не найдены обязательные колонки: {', '.join(missing)}"
    )
    st.stop()

employee_col = column_mapping["employee"]
city_col = column_mapping["city"]
manager_col = column_mapping["manager"]
status_col = column_mapping["status"]

statuses = sorted(
    df[status_col]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

st.sidebar.header("Фильтры")

selected_statuses = st.sidebar.multiselect(
    "Статусы",
    statuses,
    default=statuses
)

cities = sorted(
    df[city_col]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

selected_cities = st.sidebar.multiselect(
    "Города",
    cities,
    default=cities
)

managers = sorted(
    df[manager_col]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

selected_managers = st.sidebar.multiselect(
    "Руководители",
    managers,
    default=managers
)

filtered_df = df[
    df[status_col].astype(str).isin(selected_statuses)
]

filtered_df = filtered_df[
    filtered_df[city_col].astype(str).isin(selected_cities)
]

filtered_df = filtered_df[
    filtered_df[manager_col].astype(str).isin(selected_managers)
]

total_employees = len(df)

selected_count = len(filtered_df)

percent = (
    round(selected_count / total_employees * 100, 2)
    if total_employees > 0
    else 0
)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Всего сотрудников", total_employees)
col2.metric("По фильтру", selected_count)
col3.metric("% от общей численности", f"{percent}%")
col4.metric(
    "Городов",
    filtered_df[city_col].nunique()
)
col5.metric(
    "Руководителей",
    filtered_df[manager_col].nunique()
)

st.divider()

summary = (
    filtered_df
    .groupby([city_col, manager_col])
    .size()
    .reset_index(name="Количество")
)

summary["% от общей численности"] = round(
    summary["Количество"] / total_employees * 100,
    2
)

st.subheader("Сводная таблица")

st.dataframe(
    summary.sort_values(
        "Количество",
        ascending=False
    ),
    use_container_width=True
)

st.divider()

st.subheader("ТОП-10 городов")

top_cities = (
    filtered_df
    .groupby(city_col)
    .size()
    .reset_index(name="Количество")
    .sort_values(
        "Количество",
        ascending=False
    )
    .head(10)
)

fig_top = px.bar(
    top_cities,
    x="Количество",
    y=city_col,
    orientation="h"
)

st.plotly_chart(
    fig_top,
    use_container_width=True
)

st.divider()

st.subheader("Доля по городам")

city_share = (
    filtered_df
    .groupby(city_col)
    .size()
    .reset_index(name="Количество")
)

city_share["Процент"] = round(
    city_share["Количество"]
    / total_employees
    * 100,
    2
)

fig_share = px.pie(
    city_share,
    names=city_col,
    values="Количество"
)

st.plotly_chart(
    fig_share,
    use_container_width=True
)

st.divider()

st.subheader("Список сотрудников")

st.dataframe(
    filtered_df[
        [
            employee_col,
            city_col,
            manager_col,
            status_col
        ]
    ],
    use_container_width=True
)

output = BytesIO()

with pd.ExcelWriter(
    output,
    engine="xlsxwriter"
) as writer:

    summary.to_excel(
        writer,
        sheet_name="Сводка",
        index=False
    )

    filtered_df.to_excel(
        writer,
        sheet_name="Сотрудники",
        index=False
    )

st.download_button(
    label="📥 Скачать отчет Excel",
    data=output.getvalue(),
    file_name="LMK_Report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
```

else:
st.info(
"Загрузите Excel файл для формирования отчета"
)
