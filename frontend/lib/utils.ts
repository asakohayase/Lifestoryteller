import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const formatDate: (dateString: string) => string = (dateString) => {
  const date = new Date(dateString);
  // Adjust the date to local time without changing the date itself
  const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return localDate.toLocaleDateString('en-US', { year: 'numeric', month: '2-digit', day: '2-digit' });
};