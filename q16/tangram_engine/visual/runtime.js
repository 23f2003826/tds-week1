export function createVisualRuntime(options) {
    const { adapter, config, applyAction, maxBatchActions = 64 } = options;
    const initialState = structuredClone(options.initialState);
    let state = structuredClone(initialState);
    let revision = 0;
    const undoStack = [];
    const redoStack = [];
    const snapshot = () => ({
        state: structuredClone(state),
        revision,
        validation: adapter.validate(state, config),
    });
    const requireRevision = (expectedRevision) => {
        if (expectedRevision !== undefined && expectedRevision !== revision) {
            throw new Error("stale revision: expected " + String(expectedRevision) + ", current " + String(revision));
        }
    };
    const commit = (next) => {
        undoStack.push(structuredClone(state));
        redoStack.length = 0;
        state = structuredClone(next);
        revision += 1;
        return snapshot();
    };
    return {
        snapshot,
        dispatch(action, expectedRevision) {
            requireRevision(expectedRevision);
            return commit(applyAction(structuredClone(state), action, config));
        },
        dispatchBatch(actions, expectedRevision) {
            requireRevision(expectedRevision);
            if (actions.length < 1 || actions.length > maxBatchActions) {
                throw new Error("batch must contain 1-" + String(maxBatchActions) + " actions");
            }
            let next = structuredClone(state);
            for (const action of actions)
                next = applyAction(next, action, config);
            return commit(next);
        },
        undo() {
            const previous = undoStack.pop();
            if (!previous)
                throw new Error("nothing to undo");
            redoStack.push(structuredClone(state));
            state = previous;
            revision += 1;
            return snapshot();
        },
        redo() {
            const next = redoStack.pop();
            if (!next)
                throw new Error("nothing to redo");
            undoStack.push(structuredClone(state));
            state = next;
            revision += 1;
            return snapshot();
        },
        reset() {
            return commit(initialState);
        },
        serialize() {
            return adapter.encodeCandidate(state, config);
        },
        importEncoded(bytes) {
            return commit(adapter.decodeCandidate(bytes, config));
        },
    };
}
