import { useEffect, useState } from "react"
import { ListItem } from "./ListItem.tsx"

export interface Plot {
	id: number; // Changed to number to match SQLite AUTOINCREMENT
	plot_name: string;
	state: string;
	district: string; // Added to match schema
	crop: string;
	season: string;   // Added to match schema
	plot_yield: number; // Added to match schema
	size_ha: number;
	annual_rainfall: number;
};

export default function PlotsList() {
	const [plots, setPlots] = useState<Plot[]>([]);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		const getAllPlots = async () => {
			try {
				const API_URL = import.meta.env.VITE_API_URL;
				const token = localStorage.getItem("token");

				if (!token) {
					console.error("No token found");
					return;
				}

				const res = await fetch(`${API_URL}/plots`, {
					method: "GET",
					headers: {
						"Content-Type": "application/json",
						"Authorization": `Bearer ${token}`
					}
				});

				if (res.ok) {
					const result = await res.json();
					// 🚨 THE FIX: Backend returns a list [], not { plots: [] }
					setPlots(result);
				} else {
					console.error("Failed to fetch plots: ", res.status);
				}
			} catch (err) {
				console.error("Error while fetching user plots:", err);
			} finally {
				setLoading(false);
			}
		};

		getAllPlots();
	}, []);

	if (loading) return <div className="w-screen h-screen flex justify-center items-center">Loading your farm data...</div>;

	return (
		<div className="w-screen h-screen flex flex-col items-center bg-gray-50">
			<h1 className="text-2xl font-bold mt-10 mb-4">Your Farm Inventory</h1>
			<div className="w-[90vw] max-w-[600px] flex flex-col gap-4 p-4 overflow-y-auto">
				{plots.length > 0 ? (
					plots.map((plot) => (
						<ListItem key={plot.id} {...plot} />
					))
				) : (
					<div className="text-center text-gray-500 mt-10">
						No plots found. Add your first plot to start carbon tracking!
					</div>
				)}
			</div>
		</div>
	)
}