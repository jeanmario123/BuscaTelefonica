import re
import time
import random
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from datetime import datetime

def criar_driver_limpo():
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-popup-blocking")
    
    driver = uc.Chrome(options=options, version_main=145, use_subprocess=True)
    driver.__del__ = lambda: None
    return driver

def formatar_telefone_br(tel_raw, ddd_padrao="67"):
    """
    formata o telefone para o padrão DDI+DDD+Número (ex: 5567991709231)
    """
    if not tel_raw:
        return None

    apenas_numeros = re.sub(r'\D', '', str(tel_raw))

    # Já possui DDI 55 + DDD + Número
    if apenas_numeros.startswith("55") and len(apenas_numeros) in [12, 13]:
        return apenas_numeros

    # Possui DDD + Número (10 ou 11 dígitos)
    if len(apenas_numeros) in [10, 11]:
        return f"55{apenas_numeros}"

    # Apenas Número local sem DDD (8 ou 9 dígitos) -> insere DDD padrão
    if len(apenas_numeros) in [8, 9]:
        return f"55{ddd_padrao}{apenas_numeros}"

    return None

def extrair_dados_pagina_corrente(driver, termo):
    resultados = []
    
    for _ in range(5):
        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(0.5)

    texto_pagina = driver.find_element(By.TAG_NAME, "body").text
    linhas = [l.strip() for l in texto_pagina.split('\n') if l.strip()]
    
    padrao_tel = re.compile(r'(?:\(?\d{2}\)?\s?)?(?:9?\d{4}[-\s]?\d{4})')
    
    for i, linha in enumerate(linhas):
        match = padrao_tel.search(linha)
        if match:
            tel_encontrado = match.group(0).strip()
            
            # Aplica a formatação desejada (ex: 5567991709231)
            tel_formatado = formatar_telefone_br(tel_encontrado, ddd_padrao="67")
            
            if tel_formatado:
                nome = "Empresa sem nome"
                if i > 0 and len(linhas[i-1]) < 60 and not padrao_tel.search(linhas[i-1]):
                    nome = linhas[i-1]
                elif i > 1 and len(linhas[i-2]) < 60 and not padrao_tel.search(linhas[i-2]):
                    nome = linhas[i-2]

                if nome.lower() in ["patrocinado", "website", "rotas", "ligar"]:
                    continue

                resultados.append({
                    "numero": tel_formatado,
                    "mensagem": "",
                })
                
    return resultados

def extrair_contatos_multiabas(lista_buscas):
    buscas = [b.strip() for b in lista_buscas if b.strip()][:3]
    if not buscas:
        print("[!] Nenhuma busca válida informada.")
        return []

    print(f"\n[+] Iniciando extração rápida e direta para {len(buscas)} busca(s)...")
    driver = criar_driver_limpo()
    resultados_totais = []

    try:
        for i, termo in enumerate(buscas):
            url = f"https://www.google.com/search?q={termo.replace(' ', '+')}&tbm=lcl"
            if i == 0:
                driver.get(url)
            else:
                driver.execute_script("window.open('about:blank', '_blank');")
                driver.switch_to.window(driver.window_handles[i])
                driver.get(url)
            time.sleep(3.0)

        handles = driver.window_handles

        for idx, handle in enumerate(handles):
            driver.switch_to.window(handle)
            termo_atual = buscas[idx]
            print(f"[Aba {idx + 1}/{len(handles)}] Processando termo: '{termo_atual}'")

            pagina_atual = 1
            while pagina_atual <= 10:
                time.sleep(2.0)
                
                dados_pg = extrair_dados_pagina_corrente(driver, termo_atual)
                resultados_totais.extend(dados_pg)
                print(f" Página {pagina_atual}: {len(dados_pg)} contatos capturados.")

                try:
                    botao_proxima = driver.find_elements(By.CSS_SELECTOR, 'a#pnnext, a[aria-label*="Próxima"], a[aria-label*="Next"]')
                    if botao_proxima and botao_proxima[0].is_displayed():
                        driver.execute_script("arguments[0].click();", botao_proxima[0])
                        pagina_atual += 1
                    else:
                        print(" [!] Não há mais páginas disponíveis.")
                        break
                except Exception:
                    print(" [!] Fim das páginas atingido.")
                    break

    finally:
        try:
            driver.quit()
        except Exception:
            pass

    return resultados_totais

def salvar_planilha(dados):
    if not dados:
        print("\n[!] Nenhum contato foi extraído.")
        return

    df = pd.DataFrame(dados)
    # Garante que a coluna Numero seja tratada como Texto puro no Excel (evita notação científica no Excel)
    df['numero'] = df['numero'].astype(str)
    
    df_limpo = df.drop_duplicates(subset=['numero']).reset_index(drop=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo_saida = f"contatos_extraidos_{timestamp}.xlsx"
    
    # Salva garantindo formato de texto para os números
    with pd.ExcelWriter(arquivo_saida, engine='openpyxl') as writer:
        df_limpo.to_excel(writer, index=False)

    print(f"RASPAGEM FINALIZADA!")
    print(f"Total de {len(df_limpo)} contatos salvos em: {arquivo_saida}")

if __name__ == "__main__":
    entrada = input("Digite até 3 buscas separadas por vírgula (ex: chaveiros cg ms, petshop cg ms, autopeças cg ms): ").strip()
    
    lista = [b.strip() for b in entrada.split(',') if b.strip()]
    if lista:
        contatos = extrair_contatos_multiabas(lista)
        salvar_planilha(contatos)