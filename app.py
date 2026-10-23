from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="365 Automobile", page_icon="🚗", layout="wide")
st.title("🚗 365 Automobile — Sales & Service Dashboard")
st.write("A simple dashboard for sales enquiries, vehicle pricing and after-sales service.")
DATA=Path(__file__).parent/"data"
@st.cache_data
def load_data():
    sales=pd.read_csv(DATA/"365_Automobiles_Sales.csv")
    service=pd.read_csv(DATA/"365_Automobiles_Service.csv")
    sales["enquiry_date"]=pd.to_datetime(sales["enquiry_date"],errors="coerce")
    service["service_date"]=pd.to_datetime(service["service_date"],errors="coerce")
    return sales,service
try: sales,service=load_data()
except Exception as e: st.error(f"Could not load project data: {e}"); st.stop()

purchased=sales["purchased"].astype(str).str.strip().str.lower().eq("yes")
conversion=purchased.mean()
a,b,c,d=st.columns(4)
a.metric("Sales enquiries",f"{len(sales):,}")
b.metric("Purchases",f"{int(purchased.sum()):,}")
c.metric("Purchase rate",f"{conversion:.1%}")
d.metric("Service records",f"{len(service):,}")

st.subheader("Sales overview")
left,right=st.columns(2)
with left:
    st.bar_chart(sales["lead_source"].value_counts())
    st.caption("Enquiries by lead source")
with right:
    monthly=sales.assign(month=sales["enquiry_date"].dt.to_period("M").astype(str)).groupby("month")["purchased"].apply(lambda x:x.astype(str).str.strip().str.lower().eq("yes").mean())
    st.line_chart(monthly)
    st.caption("Monthly purchase rate")
st.subheader("Purchases by interested model")
model_rate=sales.assign(purchase_flag=purchased).groupby("model_interested")["purchase_flag"].mean().sort_values()
st.bar_chart(model_rate, horizontal=True)

st.subheader("After-sales service")
left,right=st.columns(2)
with left:
    costs=service.groupby("model")["service_cost_aed"].median().sort_values()
    st.bar_chart(costs, horizontal=True)
    st.caption("Median service cost by vehicle model (AED)")
with right:
    service["repeat_flag"]=service["repeat_visit_30_days"].astype(str).str.strip().str.lower().eq("yes")
    centres=service.groupby("service_centre").agg(repeat_rate=("repeat_flag","mean"),avg_wait_days=("workshop_wait_days","mean"),avg_satisfaction=("customer_satisfaction","mean"),visits=("service_id","count")).sort_values("repeat_rate",ascending=False)
    st.dataframe(centres.style.format({"repeat_rate":"{:.1%}","avg_wait_days":"{:.1f}","avg_satisfaction":"{:.2f}"}),use_container_width=True)

st.subheader("Filter and inspect records")
chosen=sales["model_interested"].dropna().astype(str).sort_values().unique().tolist()
selected=st.selectbox("Vehicle model",["All"]+chosen)
view=sales if selected=="All" else sales[sales["model_interested"].astype(str)==selected]
st.dataframe(view.head(100),use_container_width=True)
st.download_button("Download filtered sales CSV",view.to_csv(index=False).encode("utf-8"),file_name="filtered_sales.csv",mime="text/csv")
st.info("The dashboard summarizes historical data. Patterns can guide investigation but do not prove cause and effect.")
