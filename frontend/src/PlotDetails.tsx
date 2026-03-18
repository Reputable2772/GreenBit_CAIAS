import { useParams } from "react-router-dom";
import { useEffect,useState } from "react";
import { Card, CardBody, CardHeader } from "@heroui/react";

interface plotDetails{
	plot_name:string,
	carbon_per_ha:number,
	total_carbon:number,
	estimated_revenue_inr:number
}

export default function PlotDetails() {
	const [plotDetail,setPlotDetail]=useState<plotDetails|null>(null);

  const { id } = useParams();
  useEffect(()=>{
	  const fetchData=async ()=>{
		  try{
			  const API_URL = import.meta.env.VITE_API_URL;
			  const res = await fetch(`${API_URL}/calculate/${id}`, {
				  method: "GET",
				  headers: {
					  "Content-Type": "application/x-www-form-urlencoded", 
					  "Authorization": `Bearer ${localStorage.getItem("token")}`,
				  },
			  });
			  if(!res.ok)
				  console.log("error while fetching plot specific data");

			  const result = await res.json();
			  setPlotDetail({
				  plot_name:result.plot_name,
				  carbon_per_ha:result.carbon_per_ha,
				  total_carbon:result.total_carbon,
				  estimated_revenue_inr:result.estimated_revenue_inr
			  })
		  }catch(err){
			  console.log(`Error while getting plot data :${err}`)
		  }
	  }
	  fetchData();
  },[])

  return (
plotDetail?
(<div className="w-full min-h-screen flex flex-col items-center p-6 gap-6">

    <h1 className="text-2xl font-bold">{plotDetail.plot_name}</h1>

    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full max-w-[600px]">

      {/* Carbon per hectare */}
      <Card>
        <CardHeader>Carbon / ha</CardHeader>
        <CardBody>
          <p className="text-xl font-semibold">
            {plotDetail.carbon_per_ha} kg
          </p>
        </CardBody>
      </Card>

      {/* Total carbon */}
      <Card>
        <CardHeader>Total Carbon</CardHeader>
        <CardBody>
          <p className="text-xl font-semibold">
            {plotDetail.total_carbon} kg
          </p>
        </CardBody>
      </Card>

      {/* Revenue */}
      <Card className="col-span-1 sm:col-span-2">
        <CardHeader>Estimated Revenue</CardHeader>
        <CardBody>
          <p className="text-2xl font-bold text-green-500">
            ₹ {plotDetail.estimated_revenue_inr}
          </p>
        </CardBody>
      </Card>

    </div>
  </div>
)
:
(<div className="p-6">Loading...</div>)
  );
}
