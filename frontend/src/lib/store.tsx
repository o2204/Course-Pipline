import React, { createContext, useContext, useState, ReactNode } from "react";

interface CourseData {
    fileId?: string;
    courseName?: string;
    baseAvatarPrompt?: string;
    baseStoryboardPrompt?: string;
}

interface StoreContextType {
    courseData: CourseData | null;
    setCourseData: (data: CourseData | null) => void;
    updateCourseData: (data: Partial<CourseData>) => void;
    clearCourseData: () => void;
}

const StoreContext = createContext<StoreContextType | undefined>(undefined);

export function StoreProvider({ children }: { children: ReactNode }) {
    const [courseData, setCourseDataState] = useState<CourseData | null>(null);

    const setCourseData = (data: CourseData | null) => {
        setCourseDataState(data);
    };

    const updateCourseData = (data: Partial<CourseData>) => {
        setCourseDataState((prev) => (prev ? { ...prev, ...data } : data as CourseData));
    };

    const clearCourseData = () => {
        setCourseDataState(null);
    };

    return (
        <StoreContext.Provider
            value={{
                courseData,
                setCourseData,
                updateCourseData,
                clearCourseData,
            }}
        >
            {children}
        </StoreContext.Provider>
    );
}

export function useStore() {
    const context = useContext(StoreContext);
    if (context === undefined) {
        throw new Error("useStore must be used within a StoreProvider");
    }
    return context;
}
