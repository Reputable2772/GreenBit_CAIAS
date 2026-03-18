import { useParams, Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { Card, CardBody, CardHeader } from "@heroui/react";

interface plotDetails {
  plot_name: string;
  carbon_per_ha: number;
  total_carbon: number;
  estimated_revenue_inr: number;
  lower_carbon_ha: number;
  upper_carbon_ha: number;
  mean_carbon_ha: number;
  reliability_rating: string;
}

export default function PlotDetails() {
  const [plotDetail, setPlotDetail] = useState<plotDetails | null>(null);
  const { id } = useParams();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const API_URL = import.meta.env.VITE_API_URL;
        const res = await fetch(`${API_URL}/calculate/${id}`, {
          method: "GET",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        });

        if (!res.ok) return;
        // Inside your useEffect fetchData function:

        const result = await res.json();

        // 1. THIS PLOT'S DATA (The specific performance)
        const specificDensity = Number(result.gross_carbon_ha ?? result.carbon_per_ha ?? 0);

        // 2. REGIONAL BENCHMARK (The average for other plots in Bangalore)
        // In a real app, this comes from a global 'averages' table.
        // For the demo, we'll use a fixed regional benchmark (e.g., 17.5 Tons/ha)
        const regionalBenchmark = 17.500;

        const net = Number(result.net_tradable_credits ?? result.total_carbon ?? 0);
        const floor = regionalBenchmark * 0.95; // 5% below average
        const ceiling = regionalBenchmark * 1.05; // 5% above average

        setPlotDetail({
          plot_name: result.plot_name || "BangalorePlot1",
          carbon_per_ha: specificDensity * 1000,
          total_carbon: net * 1000,
          estimated_revenue_inr: Number(result.estimated_revenue_inr ?? 0),
          lower_carbon_ha: floor * 1000,
          upper_carbon_ha: ceiling * 1000,
          mean_carbon_ha: regionalBenchmark * 1000, // This is what creates the "Gap"
          reliability_rating: result.reliability_rating ?? "A (High)",
        });

      } catch (err) {
        console.error("Data fetching failed:", err);
      }
    };

    fetchData();
  }, [id]);

  if (!plotDetail) {
    return (
      <div className="w-full h-screen flex flex-col items-center justify-center p-6 bg-emerald-50 text-emerald-800 font-bold">
        <div className="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mb-4"></div>
        Syncing with Satellite Data...
      </div>
    );
  }

  // GAP CALCULATION LOGIC
  const { lower_carbon_ha: low, upper_carbon_ha: high, mean_carbon_ha: avg, carbon_per_ha: current } = plotDetail;

  const rate = plotDetail.total_carbon > 0
    ? (plotDetail.estimated_revenue_inr / plotDetail.total_carbon).toFixed(2)
    : "0";

  const range = high - low;
  const clampedPos = range > 0 ? Math.max(0, Math.min(100, ((current - low) / range) * 100)) : 50;
  const avgPos = range > 0 ? Math.max(0, Math.min(100, ((avg - low) / range) * 100)) : 50;

  const diffNum = current - avg;
  const isAbove = current >= avg;

  return (
    <div className="w-full min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex flex-col items-center p-6 pb-12 gap-6 overflow-y-auto font-sans">

      <div className="w-full max-w-[700px]">
        <Link to="/plots" className="text-emerald-700 hover:text-emerald-900 font-bold text-sm bg-white/40 px-4 py-2 rounded-full shadow-sm">
          ← Back to all Plots 
        </Link>
      </div>

      <div className="text-center">
        <h1 className="text-5xl font-black text-emerald-900">{plotDetail.plot_name}</h1>
        <p className="text-emerald-600 font-black uppercase text-[10px] tracking-[0.2em] mt-2">Verifiable Carbon Asset</p>
      </div>

      {/* Hero Banner */}
      <div className="w-full max-w-[700px] bg-gradient-to-r from-emerald-600 to-green-700 text-white p-10 rounded-[2.5rem] shadow-2xl text-center border-b-8 border-emerald-800">
        <p className="text-emerald-100 font-bold text-xs uppercase tracking-widest mb-2">Net Tradable Credits</p>
        <div className="text-7xl font-black tracking-tighter">
          {plotDetail.total_carbon.toLocaleString(undefined, { maximumFractionDigits: 0 })}
          <span className="text-3xl ml-3 text-emerald-300">kg CO₂</span>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full max-w-[700px]">
        <Card className="border-none shadow-xl bg-white/90">
          <CardHeader className="text-gray-400 font-black text-[10px] uppercase px-6 pt-5 pb-0">Plot Density</CardHeader>
          <CardBody className="px-6 pb-6 pt-1">
            <p className="text-4xl font-black text-gray-800">{plotDetail.carbon_per_ha.toLocaleString()}</p>
            <p className="text-[10px] text-gray-400 font-bold uppercase">kg / ha / year</p>
          </CardBody>
        </Card>

        <Card className="border-none shadow-xl bg-white/90">
          <CardHeader className="text-gray-400 font-black text-[10px] uppercase px-6 pt-5 pb-0">Market Value</CardHeader>
          <CardBody className="px-6 pb-6 pt-1">
            <p className="text-4xl font-black text-emerald-600">₹{plotDetail.estimated_revenue_inr.toLocaleString()}</p>
            <p className="text-[10px] text-gray-400 font-bold uppercase">at ₹{rate}/kg verified CO₂</p>
          </CardBody>
        </Card>
      </div>

      <div className="bg-emerald-950 text-emerald-400 px-6 py-2 rounded-full shadow-lg border border-emerald-500/30 text-[10px] font-black uppercase tracking-tighter flex items-center gap-3">
        <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse shadow-[0_0_8px_#10b981]" />
        Reliability Rating: {plotDetail.reliability_rating}
      </div>

      {/* Range Visualizer & Gap Analysis */}
      <div className="w-full max-w-[700px] bg-white p-10 rounded-[2rem] shadow-xl border border-white">
        <div className="flex justify-between items-center mb-10">
          <h2 className="text-xl font-black text-gray-800 italic">Regional Performance</h2>
          <span className={`px-4 py-1 rounded-full text-[10px] font-black uppercase ${isAbove ? 'bg-emerald-100 text-emerald-700' : 'bg-orange-100 text-orange-700'}`}>
            {isAbove ? '★ Outperforming' : 'Below Average'}
          </span>
        </div>

        <div className="relative w-full h-5 bg-gradient-to-r from-orange-200 via-yellow-100 to-emerald-400 rounded-full shadow-inner mb-12">
          {/* Legend */}
          <div className="absolute -top-7 left-0 text-[10px] font-black text-gray-300 uppercase">Min ({Math.round(low)})</div>
          <div className="absolute -top-7 right-0 text-[10px] font-black text-gray-300 uppercase">Max ({Math.round(high)})</div>

          {/* Regional Average Line */}
          <div className="absolute top-1/2 -translate-y-1/2 w-1.5 h-10 bg-gray-300 rounded-full z-10 shadow-sm" style={{ left: `${avgPos}%` }}>
            <span className="absolute top-full mt-2 left-1/2 -translate-x-1/2 text-[9px] font-black text-gray-400">REGIONAL AVG</span>
          </div>

          {/* User Marker */}
          <div className="absolute top-1/2 -translate-y-1/2 w-8 h-8 bg-white rounded-full border-[7px] border-emerald-600 shadow-2xl z-20 transition-all hover:scale-125" style={{ left: `${clampedPos}%` }}>
            <div className="absolute -top-12 left-1/2 -translate-x-1/2 bg-emerald-900 text-white text-[11px] font-black px-3 py-1.5 rounded-lg shadow-xl whitespace-nowrap">
              YOU: {Math.round(current)} kg
            </div>
          </div>
        </div>

        {/* GAP TO AVERAGE DISPLAY */}
        <div className="flex justify-between items-center border-t pt-6">
          <div className="flex flex-col">
            <p className="text-[10px] font-black text-gray-400 uppercase tracking-tighter">Gap to Average</p>
            <p className={`text-2xl font-black ${isAbove ? 'text-emerald-600' : 'text-orange-600'}`}>
              {isAbove ? '+' : ''}{diffNum.toFixed(1)} <span className="text-xs">kg / ha</span>
            </p>
          </div>
          <div className="text-right">
            <p className="text-[10px] font-black text-gray-400 uppercase tracking-tighter">Status</p>
            <p className="text-sm font-black text-gray-800 uppercase italic">
              {isAbove ? 'High Value Asset' : 'Growth Opportunity'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
