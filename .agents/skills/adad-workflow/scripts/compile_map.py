# -*- coding: utf-8 -*-
import sys
import os
import json
from adad_core import ADADCore, parse_markdown

def main():
    md_path = "system_map.md"
    yaml_path = "system_map.yaml"
    
    if not os.path.exists(md_path):
        print(json.dumps({"success": False, "error": f"找不到架構源檔案 {md_path}"}, ensure_ascii=False))
        sys.exit(1)
        
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()
    except Exception as e:
        print(json.dumps({"success": False, "error": f"讀取 {md_path} 失敗: {e}"}, ensure_ascii=False))
        sys.exit(1)
        
    # 1. 解析 Markdown
    try:
        compiled_data = parse_markdown(md_content)
    except Exception as e:
        print(json.dumps({"success": False, "error": f"解析 Markdown 失敗: {e}"}, ensure_ascii=False))
        sys.exit(1)
        
    # 驗證必要欄位
    for mod_name, mod_info in compiled_data.get("modules", {}).items():
        if not mod_info.get("type"):
            print(json.dumps({"success": False, "error": f"編譯失敗：模組 [{mod_name}] 缺少必要欄位 'Type'"}, ensure_ascii=False))
            sys.exit(1)
            
    # 2. 智慧狀態合併
    # 讀取舊的 YAML (若存在)
    core = ADADCore(yaml_path, check_validity=False)
    old_modules = core.data.get("modules", {})
    
    for mod_name, mod_info in compiled_data.get("modules", {}).items():
        # 如果舊 YAML 存在該模組
        if mod_name in old_modules:
            old_mod = old_modules[mod_name]
            # 比對結構 (input, output, dependencies)
            struct_match = (
                mod_info.get("input") == old_mod.get("input") and
                mod_info.get("output") == old_mod.get("output") and
                sorted(mod_info.get("dependencies", [])) == sorted(old_mod.get("dependencies", []))
            )
            if struct_match:
                # 結構無變動，繼承狀態
                mod_info["state"] = old_mod.get("state", "planned")
            else:
                # 結構有變動，重置為 dirty
                mod_info["state"] = "dirty"
        else:
            # 全新模組，狀態為 planned
            mod_info["state"] = "planned"
            
    # 3. 寫入並更新 YAML
    core.data["version"] = compiled_data.get("version", 1)
    core.data["modules"] = compiled_data.get("modules", {})
    core.save()
    
    # 強制確保 system_map.yaml 的修改時間稍微新於 system_map.md (大於 1.5 秒)
    # 這能確保編譯後 read_context 不會被過期阻斷判定誤導
    try:
        os.utime(yaml_path, None)
    except Exception:
        pass
        
    print(json.dumps({
        "success": True,
        "message": f"編譯成功！已將 {md_path} 編譯為 {yaml_path}，並完成狀態合併。"
    }, ensure_ascii=False, indent=2))
    sys.exit(0)

if __name__ == "__main__":
    main()
