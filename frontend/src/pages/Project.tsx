import { useParams } from 'react-router-dom';

export default function Project() {
  const { id } = useParams();

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-4">Project</h1>
      <p className="text-gray-600">Project details and chapters for {id}.</p>
    </div>
  );
}
