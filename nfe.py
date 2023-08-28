from pynfe.processamento.comunicacao import ComunicacaoSefaz
from pynfe.entidades.cliente import Cliente
from pynfe.entidades.emitente import Emitente
from pynfe.entidades.notafiscal import NotaFiscal
from pynfe.entidades.fonte_dados import _fonte_dados
from pynfe.processamento.serializacao import SerializacaoXML
from pynfe.processamento.assinatura import AssinaturaA1
from pynfe.utils.flags import CODIGO_BRASIL
from pynfe.utils.flags import NAMESPACE_NFE
from lxml import etree
from decimal import Decimal
import datetime

class NFe:
  def __init__(self):
      self.certificado = "./certificado.pfx"
      self.senha = '123456'
      self.uf = 'rs'
      self.homologacao = True
      self.a1 = AssinaturaA1(self.certificado, self.senha)
      self.emitente = Emitente(
          razao_social='NF-E EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL',
          nome_fantasia='Nome Fantasia da Empresa',
          cnpj='99999999000199',           # cnpj apenas números
          codigo_de_regime_tributario='1', # 1 para simples nacional ou 3 para normal
          inscricao_estadual='9999999999', # numero de IE da empresa
          inscricao_municipal='12345',
          cnae_fiscal='9999999',           # cnae apenas números
          endereco_logradouro='Rua da Paz',
          endereco_numero='666',
          endereco_bairro='Sossego',
          endereco_municipio='Paranavaí',
          endereco_uf='PR',
          endereco_cep='87704000',
          endereco_pais=CODIGO_BRASIL
      )

  def set_cliente(self):
    self.cliente = Cliente(
        razao_social='NF-E EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL',
        tipo_documento='CPF',           #CPF ou CNPJ
        email='email@email.com',
        numero_documento='12345678900', # numero do cpf ou cnpj
        indicador_ie=9,                 # 9=Não contribuinte 
        endereco_logradouro='Rua dos Bobos',
        endereco_numero='Zero',
        endereco_complemento='Ao lado de lugar nenhum',
        endereco_bairro='Aquele Mesmo',
        endereco_municipio='Brasilia',
        endereco_uf='DF',
        endereco_cep='12345123',
        endereco_pais=CODIGO_BRASIL,
        endereco_telefone='11912341234',
    )

  def create_nf(self):
    self.nota_fiscal = NotaFiscal(
      emitente=self.emitente,
      cliente=self.cliente,
      uf=self.uf.upper(),
      natureza_operacao='VENDA', # venda, compra, transferência, devolução, etc
      forma_pagamento=0,         # 0=Pagamento à vista; 1=Pagamento a prazo; 2=Outros.
      tipo_pagamento=1,
      modelo=55,                 # 55=NF-e; 65=NFC-e
      serie='1',
      numero_nf='111',           # Número do Documento Fiscal.
      data_emissao=datetime.datetime.now(),
      data_saida_entrada=datetime.datetime.now(),
      tipo_documento=1,          # 0=entrada; 1=saida
      municipio='4118402',       # Código IBGE do Município 
      tipo_impressao_danfe=1,    # 0=Sem geração de DANFE;1=DANFE normal, Retrato;2=DANFE normal Paisagem;3=DANFE Simplificado;4=DANFE NFC-e;
      forma_emissao='1',         # 1=Emissão normal (não em contingência);
      cliente_final=1,           # 0=Normal;1=Consumidor final;
      indicador_destino=1,
      indicador_presencial=1,
      finalidade_emissao='1',    # 1=NF-e normal;2=NF-e complementar;3=NF-e de ajuste;4=Devolução de mercadoria.
      processo_emissao='0',      #0=Emissão de NF-e com aplicativo do contribuinte;
      transporte_modalidade_frete=1,
      informacoes_adicionais_interesse_fisco='Mensagem complementar',
      totais_tributos_aproximado=Decimal('21.06'),
    )

    self.nota_fiscal.adicionar_responsavel_tecnico(
      cnpj='23025656000164',
      contato='TadaSoftware',
      email='tadasoftware@gmail.com',
      fone='11912341234'
    )


  def include_products(self, products, ncm='4901', cfop='5405', ind_total=1):
    for product in products:
      self.nota_fiscal.adicionar_produto_servico(
          codigo=product.code,                           # id do produto
          descricao=product.description,
          ncm=ncm, #ver certinho o numero
          #cest='0100100',                            # NT2015/003
          cfop=cfop,
          unidade_comercial='UN',
          ean=product.ean_13,
          ean_tributavel='SEM GTIN',
          quantidade_comercial=Decimal(product.qnt),        # 12 unidades
          valor_unitario_comercial=Decimal(product.price),  # preço unitário
          valor_total_bruto=Decimal(product.price*product.qnt),       # preço total
          unidade_tributavel='UN',
          quantidade_tributavel=Decimal('0'),
          valor_unitario_tributavel=Decimal('0'),
          ind_total=ind_total,
          # numero_pedido='12345',                   # xPed
          # numero_item='123456',                    # nItemPed
          icms_modalidade='40',
          icms_origem=0,
          icms_csosn='0',
          pis_modalidade='0',
          cofins_modalidade='0',
          valor_tributos_aprox='0'
          )

  def view_note(self):
    nf_dict = self.nota_fiscal.__dict__
    nf_dict['produtos'] = [self.nota_fiscal.produtos_e_servicos[i].__dict__ for i in range(len(self.nota_fiscal.produtos_e_servicos))]
    nf_dict['emitente'] = self.nota_fiscal.emitente.__dict__
    nf_dict['cliente'] = self.nota_fiscal.cliente.__dict__

    print(nf_dict)
    return nf_dict

  def emitir(self):
    serializador = SerializacaoXML(_fonte_dados, homologacao=self.homologacao)
    nfe = serializador.exportar()

    # assinatura
    xml = self.a1.assinar(nfe)

    # conexão
    con = ComunicacaoSefaz(self.uf, self.certificado, self.senha, self.homologacao)
    xml_response = con.status_servico('nfe')     # nfe ou nfce
    print (xml_response.text)
    
    # exemplo de leitura da resposta
    ns = {'ns': NAMESPACE_NFE }
    # algumas uf podem ser xml.text ou xml.content
    resposta = etree.fromstring(xml_response.content)[0][0]

    status = resposta.xpath('ns:retConsStatServ/ns:cStat',namespaces=ns)[0].text

    motivo = resposta.xpath('ns:retConsStatServ/ns:xMotivo',namespaces=ns)[0].text

    print(status)
    print(motivo)
    

    envio = con.autorizacao(modelo='nfe', nota_fiscal=xml)

    # em caso de sucesso o retorno será o xml autorizado
    # Ps: no modo sincrono, o retorno será o xml completo (<nfeProc> = <NFe> + <protNFe>)
    # no modo async é preciso montar o nfeProc, juntando o retorno com a NFe  
    if envio[0] == 0:
      print('Sucesso!')
      print(etree.tostring(envio[1], encoding="unicode").replace('\n','').replace('ns0:','').replace(':ns0', ''))
    # em caso de erro o retorno será o xml de resposta da SEFAZ + NF-e enviada
    else:
      print('Erro:')
      print(envio[1].text) # resposta
      print('Nota:')
      print(etree.tostring(envio[2], encoding="unicode")) # nfe

    return envio

# exemplo de nota fiscal referenciada (devolução/garantia)
# nfRef = NotaFiscalReferenciada(
#     chave_acesso='99999999999999999999999999999999999999999999')
# nota_fiscal.notas_fiscais_referenciadas.append(nfRef)

# exemplo de grupo de pessoas autorizadas a baixar xml
# autxml_lista = ['99999999000199', '00000000040']
# for index, item in enumerate(autxml_lista, 1):
#    nota_fiscal.adicionar_autorizados_baixar_xml(CPFCNPJ=item)

