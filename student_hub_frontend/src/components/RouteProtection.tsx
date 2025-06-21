import type {ReactNode} from "react";
import {Navigate} from "react-router-dom";

function isLoggedIn(): boolean {
    const email = localStorage.getItem('email');

    return email != null;
}

export function endSession(redirect: boolean = true) {
    if (isLoggedIn()) {
        localStorage.clear()
    }
    if (redirect) {
        window.location.href = import.meta.env.VITE_HOME_URL;
    }
}

export default function RouteProtection({ children, redirect }: { children: ReactNode, redirect?: string}) {
    if(!isLoggedIn()) {
        endSession(false) // param -> redirect
        return <Navigate to={redirect ? redirect : "/"} replace/>;
    } else {
        return children;
    }
}