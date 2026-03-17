import { MapContainer, TileLayer, Marker, Popup} from 'react-leaflet'
import {useEffect , useState} from 'react';
import 'leaflet/dist/leaflet.css'
import {Autocomplete, AutocompleteItem,Input,Button} from "@heroui/react";

export default function HomePage() {
	const [pos,setPos]=useState<[lat:number,lng:number]|null>(null);
	const [crops,setCrops]=useState<string[]>(['Crop1','Crop2','Crop3']);
	const [states,setStates]=useState<string[]>(['Karnataka','Bihar','Tamil Nade','Andra Pradesh']);
	const [crop,setCrop]=useState<string>("");
	const [state,setState]=useState<string>("");
	const [size_ha,setSize_ha]=useState<number>(0);
	const [plot_name,setPlot_name]=useState<string>("");

	//Getting current user location
	useEffect(()=>{
		navigator.geolocation.getCurrentPosition(
			(pos) => {
				const lat=pos.coords.latitude;
				const lng=pos.coords.longitude;
				console.log(pos);
				setPos([lat,lng])
			},
			(err) => {
				console.log(`Error while getting location ${err.message}`);
			})},[])


			useEffect(()=>{
				const fetchData = async()=>{
					try{
						const API_URL = import.meta.env.VITE_API_URL;
						const res=await fetch(`${API_URL}/metadata`)
						const result=await res.json();
						setStates(result.states);
						setCrops(result.crops);
					}catch(err){
						console.log(`Error while fetching metadata from Backend: ${err}`);
					}
				}
				fetchData();
			},[]);

			async function formSubmit( e: React.FormEvent<HTMLFormElement>){
				e.preventDefault();
				try{
					const API_URL = import.meta.env.VITE_API_URL;
					const res=await fetch(`${API_URL}/plots`,
						{
						method:"POST",
						headers:{
							"Content-Type": "application/json",
							"Authorization": `Bearer ${localStorage.getItem("token")}`,
						},
						body: JSON.stringify({
							plot_name:plot_name,
							state:state,
							crop:crop,
							size_ha:size_ha
						}),
					});
					if(!res.ok){
						console.log("There is some issue while adding the plot ");
					}
				}catch(err){ console.log(`error while adding in the plot: ${err}`); }
			}
			return (
				<div className="w-screen h-screen flex flex-col justify-center items-center">
				<div className="w-[50vw] max-w-[550px] h-screen flex flex-col items-center justify-center">
				{pos?
					<MapContainer
					center={pos}
					zoom={13}
					scrollWheelZoom={false}
					className="h-[500px] w-full"
					>
					<TileLayer
					attribution=""
					url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
					/>
					<Marker position={pos}>
					<Popup>
					Your Location
					</Popup>
					</Marker>
					</MapContainer>
						:
							<div className="h-[500px] w-full">getting location</div>
				}
				<form onSubmit={formSubmit}>
				<Input
					value={plot_name}
				  label="Plot Name"
				  labelPlacement="outside"
				  placeholder="Your Plot Name"
				  className="p-2"
				  onChange={(e) => setPlot_name(e.target.value)}
				  />

				  <div className="flex flex-row ">
					<label>
					State:
						<Autocomplete name="state" 
					className="max-w-xs p-2"
					label="State"
					selectedKey={state}
					onSelectionChange={(key) => setState(String(key))}>
					{states.map((state,index) => (
						<AutocompleteItem key={index}>{state}</AutocompleteItem>
					))}
					</Autocomplete>
					</label>

					<label>
					Crop:
						<Autocomplete name="crop"
					className="max-w-xs p-2"
					label="Crop"
					selectedKey={crop}
					onSelectionChange={(key) => setCrop(String(key))}>
					{crops.map((crop,index) => (
						<AutocompleteItem key={index}>{crop}</AutocompleteItem>
					))}
					</Autocomplete>
					</label>
				  </div>
				<Input
				  label="Size in Hectares"
				  labelPlacement="outside"
				  placeholder="0.00"
				  type="number"
				  className="p-2"
				  value={String(size_ha)}
				  onChange={(e) => setSize_ha(Number(e.target.value))}
				  />
				<Button color="primary" className="w-full p-2">Submit</Button>
				</form>
				</div>
				</div>
			)
}
