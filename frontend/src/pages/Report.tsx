import { useParams } from 'react-router-dom';

export default function Report() {
  const { id } = useParams();

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-4">QA Report</h1>
      <p className="text-gray-600">Translation quality report for project {id}.</p>
    </div>
  );
}
