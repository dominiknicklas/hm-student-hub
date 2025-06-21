import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import './index.css'
import Startup from "./pages/Startup.tsx";
import Home from "./pages/Home.tsx"
import AccessDenied from "./pages/AccessDenied.tsx";
import RouteProtection from "./components/RouteProtection.tsx";
import Professor from "./pages/Professor.tsx";


const router = createBrowserRouter([
    {
        path: "/",
        element: <Startup />
    },
    {
        path: "/home",
        element: <RouteProtection redirect={'/access-denied'}><Home/></RouteProtection>
    },
    {
        path: "/professor",
        element: <RouteProtection redirect={'/access-denied'}><Professor/></RouteProtection>
    },
    {
        path: '/access-denied',
        element: <AccessDenied/>
    },
])

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <RouterProvider router={router}/>
    </StrictMode>,
)
