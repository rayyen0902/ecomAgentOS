#[cfg_attr(mobile, tauri::mobile_entry_point)]
fn main() {
    tauri::Builder::default()
        .setup(|app| {
            // 启动Python FastAPI服务端子进程
            println!("Starting Python FastAPI service...");
            // TODO: 使用Command::new("python")启动uvicorn
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
