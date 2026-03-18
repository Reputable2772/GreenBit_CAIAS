import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import LoginPage from './LoginPage.tsx'
import HomePage from './HomePage.tsx'
import {HeroUIProvider} from "@heroui/react";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import TitleBar from "./TitleBar.tsx";
import PlotsList from "./PlotsList.tsx";
import PlotDetails from "./PlotDetails.tsx";

const router = createBrowserRouter([
  {
    path: "/",
    element: <LoginPage/>, 
  },
  {
    path: "/home",
    element: <HomePage/>, 
  },
  {
	  path:"/plots",
	  element:<PlotsList/>
  },
  {
	  path: "/plots/:id",   
	  element: <PlotDetails />,
  },
]);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
  <HeroUIProvider>
  <main className="h-screen text-foreground bg-background overflow-y-hidden">
  <TitleBar/>
  <RouterProvider router={router} />
  </main>
  </HeroUIProvider>
  </StrictMode>,
)
