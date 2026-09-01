import { Routes, Route } from 'react-router-dom';
import { SignedIn, SignedOut, RedirectToSignIn } from '@clerk/clerk-react';
import HomePage from './pages/HomePage';
import SignIn from './pages/SignIn';
import SignUp from './pages/SignUp';
import DashboardPage from './pages/DashboardPage';
import PricingPage from './pages/PricingPage';

function ProtectedRoute({ children }) {
    return (
        <>
            <SignedIn>{children}</SignedIn>
            <SignedOut>
                <RedirectToSignIn />
            </SignedOut>
        </>
    );
}

function App() {
    return (
        <Routes>
            <Route path={'/'}>
                <Route index element={<HomePage />} />
                <Route path={'sign-in/*'} element={<SignIn />} />
                <Route path={'sign-up/*'} element={<SignUp />} />
                <Route path={'pricing'} element={<PricingPage />} />
                <Route
                    path={'dashboard'}
                    element={
                        <ProtectedRoute>
                            <DashboardPage />
                        </ProtectedRoute>
                    }
                />
            </Route>
        </Routes>
    );
}

export default App;
