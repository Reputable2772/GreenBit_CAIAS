import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { useEffect, useState } from 'react';
import 'leaflet/dist/leaflet.css';
import { Autocomplete, AutocompleteItem, Input, Button } from "@heroui/react";
import { Link } from "react-router-dom";

export default function HomePage() {
	const [pos, setPos] = useState<[number, number] | null>(null);
	const [crops, setCrops] = useState<string[]>([]);
	const [states, setStates] = useState<string[]>([]);
	const [districts, setDistricts] = useState<string[]>([]);
	const [seasons, setSeasons] = useState<string[]>([]);

	// Form States (Stripped down to only what user provides)
	const [plot_name, setPlot_name] = useState("");
	const [state, setState] = useState("");
	const [district, setDistrict] = useState("");
	const [crop, setCrop] = useState("");
	const [season, setSeason] = useState("");
	const [size_ha, setSize_ha] = useState(0);

	// 1. Get Current Location for the Map
	useEffect(() => {
		navigator.geolocation.getCurrentPosition(
			(pos) => setPos([pos.coords.latitude, pos.coords.longitude]),
			(err) => console.error(`Location Error: ${err.message}`)
		);
	}, []);

	// 2. Fetch Metadata for Dropdowns
	useEffect(() => {
		const fetchMetadata = async () => {
			try {
				const API_URL = import.meta.env.VITE_API_URL;
				const res = await fetch(`${API_URL}/metadata`);
				const data = await res.json();
				setStates(data.states);
				setCrops(data.crops);
				setDistricts(data.districts);
				setSeasons(data.seasons);
			} catch (err) {
				console.error("Metadata fetch failed", err);
			}
		};
		fetchMetadata();
	}, []);

	// 3. Submit Plot (Internal lookup happens on backend)
	async function formSubmit(e: React.FormEvent<HTMLFormElement>) {
		e.preventDefault();
		try {
			const API_URL = import.meta.env.VITE_API_URL;
			const res = await fetch(`${API_URL}/plots`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"Authorization": `Bearer ${localStorage.getItem("token")}`,
				},
				body: JSON.stringify({
					plot_name,
					state,
					district,
					crop,
					season,
					size_ha
				}),
			});

			if (res.ok) {
				alert("Analysis Complete! Environmental data matched and plot saved.");
				// Clear form or redirect
				setPlot_name("");
				setSize_ha(0);
			} else {
				console.error("Failed to add plot. Check if all fields are selected.");
			}
		} catch (err) {
			console.error("Error submitting plot:", err);
		}
	}

	return (
<div className="w-full h-full flex flex-col items-center p-6 bg-gray-50 overflow-y-auto">
<div className="w-[90vw] max-w-[900px] flex flex-col items-center gap-6 pb-10">

				<h1 className="text-3xl font-bold text-green-700">New Carbon Analysis</h1>

				{/* Map Section */}
				<div className="h-[350px] w-full rounded-2xl overflow-hidden shadow-xl border-4 border-white">
					{pos ? (
						<MapContainer center={pos} zoom={13} className="h-full w-full">
							<TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
							<Marker position={pos}>
								<Popup>Current Location</Popup>
							</Marker>
						</MapContainer>
					) : (
						<div className="flex items-center justify-center h-full bg-gray-200 animate-pulse">
							Initializing Satellite Link...
						</div>
					)}
				</div>

				{/* Simplified Form Section */}
				<form onSubmit={formSubmit} className="w-full bg-white p-8 rounded-2xl shadow-sm grid grid-cols-2 gap-6">
					<Input
						className="col-span-2"
						label="Plot Identifier"
						placeholder="e.g. West Punjab Field B"
						value={plot_name}
						onChange={(e) => setPlot_name(e.target.value)}
						required
					/>

					<Autocomplete label="State" selectedKey={state} onSelectionChange={(k) => setState(String(k))} required>
						{states.map((s) => <AutocompleteItem key={s} value={s}>{s}</AutocompleteItem>)}
					</Autocomplete>

					<Autocomplete label="District" selectedKey={district} onSelectionChange={(k) => setDistrict(String(k))} required>
						{districts.map((d) => <AutocompleteItem key={d} value={d}>{d}</AutocompleteItem>)}
					</Autocomplete>

					<Autocomplete label="Crop Type" selectedKey={crop} onSelectionChange={(k) => setCrop(String(k))} required>
						{crops.map((c) => <AutocompleteItem key={c} value={c}>{c}</AutocompleteItem>)}
					</Autocomplete>

					<Autocomplete label="Growth Season" selectedKey={season} onSelectionChange={(k) => setSeason(String(k))} required>
						{seasons.map((s) => <AutocompleteItem key={s} value={s}>{s}</AutocompleteItem>)}
					</Autocomplete>

					<Input
						className="col-span-2"
						label="Plot Size (Hectares)"
						type="number"
						step="0.01"
						placeholder="0.00"
						value={String(size_ha)}
						onChange={(e) => setSize_ha(Number(e.target.value))}
						required
					/>

					<Button
						color="success"
						type="submit"
						className="col-span-2 h-14 text-white font-bold text-lg shadow-lg hover:scale-[1.01] transition-transform"
					>
						⚡ Run AI Carbon Sequestration Analysis
					</Button>
				</form>
				<Link to="/plots" className="w-full">
				<Button color="primary" variant="faded" className="w-full">
				View All Plots
				</Button>
				</Link>
			</div>
		</div>
	);
}
