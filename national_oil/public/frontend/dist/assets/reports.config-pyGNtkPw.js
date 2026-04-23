const e=()=>new Date().toISOString().slice(0,10),t=()=>new Date(new Date().getFullYear(),new Date().getMonth(),1).toISOString().slice(0,10),l=()=>new Date().getFullYear(),r=()=>new Date().getMonth()+1,n=[{slug:"daily-sales-summary",name:"Daily Sales Summary",category:"Sales",filters:[{name:"dated",label:"Date",type:"Date",default:e()},{name:"department",label:"Department",type:"Link",options:"Department"},{name:"sale_type",label:"Sale Type",type:"Select",options:`
Wet Stock
Other`}]},{slug:"weekly-sales-summary",name:"Weekly Sales Summary",category:"Sales",filters:[{name:"from_date",label:"From Date",type:"Date",default:t()},{name:"to_date",label:"To Date",type:"Date",default:e()},{name:"department",label:"Department",type:"Link",options:"Department"}]},{slug:"monthly-sales-summary",name:"Monthly Sales Summary",category:"Sales",filters:[{name:"year",label:"Year",type:"Int",default:l()},{name:"month",label:"Month",type:"Select",options:`
1
2
3
4
5
6
7
8
9
10
11
12`},{name:"department",label:"Department",type:"Link",options:"Department"}]},{slug:"annual-sales-summary",name:"Annual Sales Summary",category:"Sales",filters:[{name:"year",label:"Year",type:"Int",default:l()},{name:"department",label:"Department",type:"Link",options:"Department"}]},{slug:"wet-stock-sales",name:"Wet Stock Sales",category:"Sales",filters:[{name:"from_date",label:"From Date",type:"Date",default:t()},{name:"to_date",label:"To Date",type:"Date",default:e()},{name:"department",label:"Department",type:"Link",options:"Department"}]},{slug:"other-sales",name:"Other Sales",category:"Sales",filters:[{name:"from_date",label:"From Date",type:"Date",default:t()},{name:"to_date",label:"To Date",type:"Date",default:e()},{name:"department",label:"Department",type:"Link",options:"Department"}]},{slug:"customer-debt-ageing",name:"Customer Debt Ageing",category:"Receivables",filters:[{name:"as_of_date",label:"As Of Date",type:"Date",default:e(),required:!0},{name:"customer",label:"Customer",type:"Link",options:"Customer"}]},{slug:"all-customer-debts",name:"All Customer Debts",category:"Receivables",filters:[{name:"customer",label:"Customer",type:"Link",options:"Customer"},{name:"status",label:"Status",type:"Select",options:`
Open
Partial
Settled`}]},{slug:"debt-collection-summary",name:"Debt Collection Summary",category:"Receivables",filters:[{name:"from_date",label:"From Date",type:"Date",default:t()},{name:"to_date",label:"To Date",type:"Date",default:e()},{name:"customer",label:"Customer",type:"Link",options:"Customer"}]},{slug:"supplier-payables",name:"Supplier Payables",category:"Payables",filters:[{name:"supplier",label:"Supplier",type:"Link",options:"Supplier"},{name:"status",label:"Status",type:"Select",options:`
Open
Partial
Settled`}]},{slug:"all-credits",name:"All Credits",category:"Payables",filters:[{name:"supplier",label:"Supplier",type:"Link",options:"Supplier"},{name:"from_date",label:"From Date",type:"Date",default:t()},{name:"to_date",label:"To Date",type:"Date",default:e()}]},{slug:"petty-cash-daily",name:"Petty Cash — Daily",category:"Finance",filters:[{name:"dated",label:"Date",type:"Date",default:e(),required:!0}]},{slug:"petty-cash-monthly",name:"Petty Cash — Monthly",category:"Finance",filters:[{name:"year",label:"Year",type:"Int",default:l()},{name:"month",label:"Month",type:"Select",options:`
1
2
3
4
5
6
7
8
9
10
11
12`,default:r()}]},{slug:"petty-cash-annual",name:"Petty Cash — Annual",category:"Finance",filters:[{name:"year",label:"Year",type:"Int",default:l()}]},{slug:"fuel-delivery-log",name:"Fuel Delivery Log",category:"Fuel",filters:[{name:"from_date",label:"From Date",type:"Date",default:t()},{name:"to_date",label:"To Date",type:"Date",default:e()},{name:"supplier",label:"Supplier",type:"Link",options:"Supplier"},{name:"fuel_type",label:"Fuel Type",type:"Link",options:"Fuel Type"}]},{slug:"fuel-stock-summary",name:"Fuel Stock Summary",category:"Fuel",filters:[{name:"fuel_type",label:"Fuel Type",type:"Link",options:"Fuel Type"}]},{slug:"pump-reading-reconciliation",name:"Pump Reading Reconciliation",category:"Fuel",filters:[{name:"from_date",label:"From Date",type:"Date",default:t()},{name:"to_date",label:"To Date",type:"Date",default:e()},{name:"pump_number",label:"Pump Number",type:"Data"},{name:"fuel_type",label:"Fuel Type",type:"Link",options:"Fuel Type"}]},{slug:"attendance-summary",name:"Attendance Summary",category:"HR",filters:[{name:"year",label:"Year",type:"Int",default:l(),required:!0},{name:"month",label:"Month",type:"Select",options:`1
2
3
4
5
6
7
8
9
10
11
12`,default:r(),required:!0},{name:"employee",label:"Employee",type:"Link",options:"NO Employee"}]},{slug:"performance-report",name:"Performance Report",category:"HR",filters:[{name:"employee",label:"Employee",type:"Link",options:"NO Employee"},{name:"from_date",label:"From Date",type:"Date",default:t()},{name:"to_date",label:"To Date",type:"Date",default:e()}]},{slug:"leave-register",name:"Leave Register",category:"HR",filters:[{name:"year",label:"Year",type:"Int",default:l()},{name:"employee",label:"Employee",type:"Link",options:"NO Employee"},{name:"status",label:"Status",type:"Select",options:`
Pending
Approved
Rejected`}]}],p=Object.fromEntries(n.map(a=>[a.slug,a])),s=[...new Set(n.map(a=>a.category))],y=s.reduce((a,o)=>(a[o]=n.filter(m=>m.category===o),a),{});export{s as C,y as R,p as a};
