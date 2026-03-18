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
            "Content-Type": "application/x-www-form-urlencoded",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        });

        if (!res.ok) return;

        const result = await res.json();

        setPlotDetail({
          plot_name: result.plot_name,
          carbon_per_ha: Number(result.carbon_per_ha ?? 0),
          total_carbon: Number(result.total_carbon ?? 0),
          estimated_revenue_inr: Number(result.estimated_revenue_inr ?? 0),

          // 🔥 convert to SAME UNIT (kg)
          lower_carbon_ha: Number(result.lower_carbon_ha ?? 0) * 1000,
          upper_carbon_ha: Number(result.upper_carbon_ha ?? 0) * 1000,
          mean_carbon_ha: Number(result.mean_carbon_ha ?? 0) * 1000,
        });

      } catch (err) {
        console.log(err);
      }
    };

    fetchData();
  }, [id]);

  if (!plotDetail) return <div className="p-6">Loading...</div>;

  const rate =
    plotDetail.total_carbon > 0
      ? (plotDetail.estimated_revenue_inr / plotDetail.total_carbon).toFixed(2)
      : "0";

  const lower = plotDetail.lower_carbon_ha;
  const upper = plotDetail.upper_carbon_ha;
  const mean = plotDetail.mean_carbon_ha;
  const value = plotDetail.carbon_per_ha;

  const range = upper - lower;

  const percent = range > 0 ? ((value - lower) / range) * 100 : 50;
  const avgPercent = range > 0 ? ((mean - lower) / range) * 100 : 50;

  const clamped = Math.max(0, Math.min(100, percent));
  const avgClamped = Math.max(0, Math.min(100, avgPercent));

  const diffNum = value - mean;

  const positionText =
    value < mean
      ? "below average"
      : value > mean
      ? "above average"
      : "around average";

  return (
    <div className="w-full h-full flex flex-col items-center p-6 pb-10 gap-6 overflow-y-auto">

      <h1 className="text-3xl font-bold text-green-700">
        🌾 {plotDetail.plot_name}
      </h1>

      <div className="w-full max-w-[600px] bg-green-100 text-green-800 p-4 rounded-xl text-center font-semibold">
        🌍 {plotDetail.total_carbon} kg CO₂ absorbed annually
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full max-w-[600px]">

        <Card>
          <CardHeader>Carbon / ha</CardHeader>
          <CardBody>
            <p className="text-3xl font-bold text-green-600">
              {plotDetail.carbon_per_ha}
            </p>
            <p className="text-sm text-gray-500">
              kg per hectare annually
            </p>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>Total Carbon</CardHeader>
          <CardBody>
            <p className="text-3xl font-bold">
              {plotDetail.total_carbon}
            </p>
            <p className="text-sm text-gray-500">
              kg CO₂ annually
            </p>
          </CardBody>
        </Card>

        <Card className="col-span-1 sm:col-span-2">
          <CardHeader>Estimated Revenue</CardHeader>
          <CardBody>
            <p className="text-3xl font-bold text-green-500">
              ₹ {plotDetail.estimated_revenue_inr}
            </p>
            <p className="text-sm text-gray-500">
              ₹ {rate} per kg CO₂
            </p>
          </CardBody>
        </Card>
      </div>

      {/* FIXED RANGE */}
      <div className="w-full max-w-[600px] bg-white p-5 rounded-xl shadow-sm">

        <h2 className="font-semibold mb-2">
          Your position in regional range
        </h2>

        <p className="text-xs text-gray-500 mb-3">
          Carbon absorption (kg per hectare)
        </p>

        <div className="flex justify-between text-xs text-gray-500 mb-2">
          <span>Low ({Math.round(lower)})</span>
          <span>Avg ({Math.round(mean)})</span>
          <span>High ({Math.round(upper)})</span>
        </div>

        <div className="relative w-full h-3 bg-gray-200 rounded-full">

          <div
            className="absolute top-1/2 -translate-y-1/2 w-1 h-5 bg-gray-400"
            style={{ left: `${avgClamped}%` }}
          />

          <div
            className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-green-500 rounded-full border-2 border-white shadow"
            style={{ left: `${clamped}%` }}
          />
        </div>

        <p className="text-sm text-gray-600 mt-4">
          Your plot is <span className="font-semibold">{positionText}</span>
        </p>

        <p className="text-xs text-gray-500">
          {diffNum > 0 ? "+" : ""}
          {diffNum.toFixed(2)} kg/ha vs average
        </p>
      </div>

      <div className="w-full max-w-[600px] flex justify-between items-center">
        <p className="text-sm text-gray-500">
          Based on regional agricultural data
        </p>

        <Link to="/plots" className="text-green-600 font-medium">
          ← Back to plots
        </Link>
      </div>
    </div>
  );
}
