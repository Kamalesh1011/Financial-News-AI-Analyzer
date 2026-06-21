import toast from "react-hot-toast";

export function showToast(message: string, type: "success" | "error" | "info" = "info") {
  switch (type) {
    case "success":
      toast.success(message, {
        style: {
          background: "rgba(31, 31, 37, 0.9)",
          color: "#fff",
          border: "1px solid rgba(34, 197, 94, 0.3)",
          backdropFilter: "blur(20px)",
        },
      });
      break;
    case "error":
      toast.error(message, {
        style: {
          background: "rgba(31, 31, 37, 0.9)",
          color: "#fff",
          border: "1px solid rgba(239, 68, 68, 0.3)",
          backdropFilter: "blur(20px)",
        },
      });
      break;
    default:
      toast(message, {
        style: {
          background: "rgba(31, 31, 37, 0.9)",
          color: "#fff",
          border: "1px solid rgba(0, 240, 255, 0.3)",
          backdropFilter: "blur(20px)",
        },
      });
  }
}
