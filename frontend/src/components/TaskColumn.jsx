import TaskCard from './TaskCard';

const STATUS_LABELS = {
    pending: 'To Do',
    in_progress: 'In Progress',
    done: 'Done',
};
const TaskColumn = ({ status, tasks, onEdit, onDelete }) => {
    return (
        <div className={'kanban-column'}>
            <div
                className={`kanban-column-header kanban-column-header-${status}`}
            >
                <h3 className={'kanban-column-title'}>
                    {STATUS_LABELS[status]}
                </h3>
                <span className={'kanban-column-count'}>{tasks.length}</span>
            </div>
            <div className={'kanban-column-body'}>
                {tasks.map((task) => (
                    <TaskCard
                        key={task.id}
                        task={task}
                        onEdit={onEdit}
                        onDelete={onDelete}
                    />
                ))}
            </div>
        </div>
    );
};

export default TaskColumn;
