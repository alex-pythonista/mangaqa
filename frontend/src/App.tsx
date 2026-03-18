import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Project from './pages/Project';
import Upload from './pages/Upload';
import Report from './pages/Report';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/projects/:id" element={<Project />} />
          <Route path="/projects/:id/upload" element={<Upload />} />
          <Route path="/projects/:id/report" element={<Report />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
