from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime

# Configuración
CSV_TARJETAS = "tarjetas_generadas.csv"
BIN = "411111"  # BIN de ejemplo (VISA). Usa "" para random.

def generar_tarjetas():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # 1. Navegar a la página
        page.goto("https://namso.net/")
        
        # 2. Rellenar BIN (si se especifica)
        if BIN:
            page.fill('input[name="form.bin"]', BIN)
        
        # 3. Seleccionar fecha (opcional: comentar para random)
        page.select_option('select[name="form.expirationDateMonth"]', value="12")  # Diciembre
        page.select_option('select[name="form.expirationDateYear"]', value="2025")  # Año 2025
        
        # 4. Hacer clic en "Generate"
        page.click('xpath=//span[text()="Generate"]')
        
        # 5. Esperar a que se generen las tarjetas
        page.wait_for_selector('xpath=//span[text()="Generate"]')  # Cuando el botón vuelve a "Generate"
        
        # 6. Extraer datos de la tabla
        tarjetas = []
        filas = page.locator("table tbody tr").all()
        for fila in filas:
            datos = fila.locator("td").all()
            tarjetas.append({
                "numero": datos[0].inner_text(),
                "tipo": datos[1].inner_text(),
                "banco": datos[2].inner_text(),
                "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        
        # 7. Guardar en CSV
        df = pd.DataFrame(tarjetas)
        try:
            df_existente = pd.read_csv(CSV_TARJETAS)
            df_final = pd.concat([df_existente, df])
        except FileNotFoundError:
            df_final = df
        
        df_final.to_csv(CSV_TARJETAS, index=False)
        print(f"✅ {len(tarjetas)} tarjetas guardadas en {CSV_TARJETAS}")
        
        browser.close()

# Ejecutar
generar_tarjetas()
