import {useEffect,useState} from "react"
import {ListItem} from "./ListItem.tsx"

export interface Plot{
	id:string,
	plot_name:string,
	state:string,
	crop:string,
	size_ha:number,
	annual_rainfall:number,
};


export default function PlotsList(){
	const [plots,setPlots]=useState<Plot[]>([
  {
    id: "1",
    plot_name: "Green Valley",
    state: "Karnataka",
    crop: "Rice",
    size_ha: 2.5,
    annual_rainfall: 1200,
  },
  {
    id: "2",
    plot_name: "Sunrise Farm",
    state: "Tamil Nadu",
    crop: "Wheat",
    size_ha: 1.8,
    annual_rainfall: 900,
  },
  {
    id: "3",
    plot_name: "River Edge",
    state: "Andhra Pradesh",
    crop: "Sugarcane",
    size_ha: 3.2,
    annual_rainfall: 1100,
  },
  {
    id: "4",
    plot_name: "Dryland Field",
    state: "Bihar",
    crop: "Maize",
    size_ha: 2.0,
    annual_rainfall: 800,
  },
])
		useEffect(()=>{
			const getAllPlots=async ()=>{
				const API_URL = import.meta.env.VITE_API_URL;
				const res=await fetch(`${API_URL}/plots`,{
					method:"GET",
					headers:{
						"Content-Type":"application/json",
						"Authorization":`Bearer ${localStorage.getItem("token")}`
					}
				})
				if(!res.ok){
					console.log("Error while fetching all the user plots")
				}else{
					const result=await res.json();
					setPlots(result.plots);
				}
			}
			getAllPlots();

		},[])
	return(
		<div className="w-screen h-screen flex flex-col justify-center items-center overflow-y-hidden">
		<div className="w-[50vw] max-w-[550px] h-full overflow-y-auto flex flex-col gap-4 p-4">
		{ 
			plots &&
				plots.map( (plot)=> <ListItem key={plot.id}  {...plot}/> )
		}
		</div>
		</div>
	)
}
