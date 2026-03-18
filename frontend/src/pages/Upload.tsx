import { useParams } from 'react-router-dom';

export default function Upload() {
  const { id } = useParams();

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-4">Upload Chapter</h1>
      <p className="text-gray-600">Upload translated manga JSON for project {id}.</p>
    </div>
  );
}
