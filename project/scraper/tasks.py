from celery import shared_task
from .views import get_news_links_azertag,get_news_links_bbc,get_news_links_sputnikarm,get_news_links_civilge,get_news_links_trthaber,get_news_links_internethaber
from django.db.models import Q
from scraper.sites.oxu_az import get_news_links_oxu
from scraper.sites.apa_az import get_news_links_apa
from scraper.sites.report_az import get_news_links_report
from scraper.sites.editor_az import get_news_links_editor
from scraper.sites.azxeber_az import get_news_links_azxeber
from scraper.sites.lent_az import get_news_links_lent
from scraper.sites.metbuat_az import get_news_links_metbuat
from scraper.sites.baku_ws import get_news_links_bakuws
from scraper.sites.xezerxeber_az import get_news_links_xezerxeber
from scraper.sites.trend_az import get_news_links_trend
from scraper.sites.milli_az import get_news_links_milli
from scraper.sites.armeniatoday_am import get_news_links_armeniatoday
from scraper.sites.lenta_ru import get_news_links_lentaru
from scraper.sites.iz_ru import get_news_links_izru
from scraper.sites.infox_ru import get_news_links_infoxru
from scraper.sites.sozcu_com_tr import get_news_links_sozcu
from scraper.sites.cumhuriyet_com_tr import get_news_links_cumhuriyet
from scraper.sites.samanyoluhaber_com_tr import get_news_links_samanyoluhaber
from scraper.sites.sabah_com_tr import get_news_links_sabah
from scraper.sites.gercekgundem_com import get_news_links_gercekgundem
from scraper.sites.agos_com_tr import get_news_links_agos
from scraper.sites.birgun_net import get_news_links_birgun
from scraper.sites.bianet_org import get_news_links_bianet
from scraper.sites.voaturkce_com import get_news_links_voaturkce
from scraper.sites.anlatilaninotesi_com_tr import get_news_links_anlatilaninotesi
from scraper.sites.dw_com import get_news_links_dwcom
from scraper.sites.ulusal_com_tr import get_news_links_ulusal
from scraper.sites.haberler_com import get_news_links_haberler
from scraper.sites.rasthaber_com import get_news_links_rasthaber
from scraper.sites.yeniakit_com_tr import get_news_links_yeniakit
from scraper.sites.yenisafak_com import get_news_links_yenisafak
from scraper.sites.milliyet_com_tr import get_news_links_milliyet
from scraper.sites.hdp_org_tr import get_news_links_hdp
from scraper.sites.aa_com_tr import get_news_links_aa
from scraper.sites.kronos38_news import get_news_links_kronos38
from scraper.sites.unian_net import get_news_links_unian_net
from scraper.sites.belta_by import get_news_links_belta_by
from scraper.sites.rbc_ua import get_news_links_rbc_ua
from scraper.sites.tass_ru import get_news_links_tass_ru
from scraper.sites.nv_ua import get_news_links_nv_ua
from scraper.sites.az_sputniknews_ru import get_news_links_az_sputniknews_ru
from scraper.sites.centralasia_media import get_news_links_centralasia_media
from scraper.sites.gazeta_uz import get_news_links_gazeta_uz
from scraper.sites.nur_kz import get_news_links_nur_kz  
from scraper.sites.orda_kz import get_news_links_orda_kz
from scraper.sites.kaztag_kz import get_news_links_kaztag_kz
from scraper.sites.uz_sputniknews_ru import get_news_links_uz_sputniknews_ru
from scraper.sites.am_sputniknews_ru import get_news_links_am_sputniknews_ru
from scraper.sites.sputnik_georgia_ru import get_news_links_sputnik_georgia_ru
from scraper.sites.norharatch_com import get_news_links_norharatch_com
from scraper.sites.newsgeorgia_ge import get_news_links_newsgeorgia_ge
from scraper.sites.mtavari_tv import get_news_links_mtavari_tv
from scraper.sites.formulanews_ge import get_news_links_formulanews_ge
from scraper.sites.arm_sputniknews_ru import get_news_links_arm_sputniknews_ru
from scraper.sites.yerevan_today import get_news_links_yerevan_today
from scraper.sites.newsarmenia_am import get_news_links_newsarmenia_am
from scraper.sites.aravot_am import get_news_links_aravot_am
from scraper.sites.infoport_am import get_news_links_infoport_am
from scraper.sites.armenpress_am import get_news_links_armenpress_am
from scraper.sites.arminfo_info import get_news_links_arminfo_info
from scraper.sites.armenianweekly_com import get_news_links_armenianweekly_com
from scraper.sites.irna_ir import get_news_links_irna_ir
from scraper.sites.alef_ir import get_news_links_alef_ir
from scraper.sites.etemadonline_com import get_news_links_etemadonline_com
from scraper.sites.esnafnews_com import get_news_links_esnafnews_com
from scraper.sites.donya_e_eqtesad_com import get_news_links_donya_e_eqtesad_com
from scraper.sites.entekhab_ir import get_news_links_entekhab_ir
from scraper.sites.irdiplomacy_ir import get_news_links_irdiplomacy_ir
from scraper.sites.kayhan_london import get_news_links_kayhan_london
from scraper.sites.sedayemardom_net import get_news_links_sedayemardom_net
from scraper.sites.zeitoons_com import get_news_links_zeitoons_com
from scraper.sites.fararu_com import get_news_links_fararu_com
from scraper.sites.ilna_ir import get_news_links_ilna_ir
from scraper.sites.hamshahrionline_ir import get_news_links_hamshahrionline_ir
from scraper.sites.khabaronline_ir import get_news_links_khabaronline_ir
from scraper.sites.mehrnews_com import get_news_links_mehrnews_com
from scraper.sites.mashreghnews_ir import get_news_links_mashreghnews_ir
from scraper.sites.aftabnews_ir import get_news_links_aftabnews_ir
from scraper.sites.tejaratnews_com import get_news_links_tejaratnews_com
from scraper.sites.mojnews_com import get_news_links_mojnews_com
from scraper.sites.atna_atu_ac_ir import get_news_links_atna_atu_ac_ir
from scraper.sites.melliun_org import get_news_links_melliun_org
from scraper.sites.isna_ir import get_news_links_isna_ir
from scraper.sites.npr_org import get_news_links_npr_org
from scraper.sites.calmatters_org import get_news_links_calmatters_org
from scraper.sites.foxnews_com import get_news_links_foxnews_com
from scraper.sites.huffpost_com import get_news_links_huffpost_com
from scraper.sites.kqed_org import get_news_links_kqed_org
from scraper.sites.pbs_org import get_news_links_pbs_org
from scraper.sites.nbcnews_com import get_news_links_nbcnews_com
from scraper.sites.news_sky_com import get_news_links_skynews_com
from scraper.sites.theguardian_com import get_news_links_theguardian_com
from scraper.sites.theconversation_com import get_news_links_theconversation_com    
from scraper.sites.vox_com import get_news_links_vox_com    
from scraper.sites.independent_co_uk import get_news_links_independent_co_uk
from scraper.sites.msnbc_com import get_news_links_msnbc_com
from scraper.sites.newsweek_com import get_news_links_newsweek_com
from scraper.sites.thehindu_com import get_news_links_thehindu_com   
from scraper.sites.yahoo_com import get_news_links_yahoo_com
from scraper.sites.boston_com import get_news_links_boston_com
from scraper.sites.greatreporter_com import get_news_links_greatreporter_com
from scraper.sites.cbsnews_com import get_news_links_cbsnews_com
from scraper.sites.ipsnews_net import get_news_links_ipsnews_net
from scraper.sites.upi_com import get_news_links_upi_com
from scraper.sites.sbs_com_au import get_news_links_sbs_com_au
from scraper.sites.latimes_com import get_news_links_latimes_com
from scraper.sites.thedispatch_com import get_news_links_thedispatch_com
from scraper.sites.globalnews_ca import get_news_links_globalnews_ca
from scraper.sites.chp_org_tr import get_news_links_chp_org_tr
from scraper.sites.nydailynews_com import get_news_links_nydailynews_com
from scraper.sites.iyiparti_org_tr import get_news_links_iyiparti_org_tr
from scraper.sites.tr_euronews_com import get_news_links_tr_euronews_com
from scraper.sites.news24_ge import get_news_links_24news_ge
from scraper.sites.interpressnews_ge import get_news_links_interpressnews_ge
from scraper.sites.aysor_am import get_news_links_aysor_am
from scraper.sites.tert_am import get_news_links_tert_am
from scraper.sites.qomnews_ir import get_news_links_qomnews_ir
from scraper.sites.iribnews_ir import get_news_links_iribnews_ir
from scraper.sites.news_gooya_ir import get_news_links_goyanews_com
from scraper.sites.tasnimnews_com import get_news_links_tasnimnews_com
from scraper.sites.tabnak_ir import get_news_links_tabnak_ir
from scraper.sites.qafqazagency_ir import get_news_links_qafqazagency_ir
from scraper.sites.gunaz_tv import get_news_links_gunaz_tv
from scraper.sites.gadtb_com import get_news_links_gadtb_com
from scraper.sites.hoosk_ir import get_news_links_hoosk_ir
from scraper.sites.tehranprelacy_com import get_news_links_tehranprelacy_com
from scraper.sites.rokna_net import get_news_links_rokna_net
from scraper.sites.jamejamonline_ir import get_news_links_jamejamonline_ir
from scraper.sites.fardanews_com import get_news_links_fardanews_com
from scraper.sites.dailymail_co_uk import get_news_links_dailymail_co_uk
from scraper.sites.bbc_com import get_news_links_bbc_com
from scraper.sites.slate_com import get_news_links_slate_com
from scraper.sites.nypost_com import get_news_links_nypost_com
from scraper.sites.chicagotribune_com import get_news_links_chicagotribune_com
from scraper.sites.radiozamaneh_com import get_news_links_radiozamaneh_com
from scraper.sites.bbcpersian_com import get_news_links_bbcpersian_com
from scraper.sites.farsnews_ir import get_news_links_farsnews_ir
from scraper.sites.rfi_fr import get_news_links_rfi_fr_fa
from scraper.sites.iranwire_com import get_news_links_iranwire_com_en
from scraper.sites.avatoday_net import get_news_links_avatoday_net
from scraper.sites.balatarin_com import get_news_links_balatarin_com
from scraper.sites.english_alarabiye_net import get_news_links_english_alarabiya_net
from scraper.sites.iranintl_com import get_news_links_iranintl_com
from scraper.sites.mirrorspectator_com import get_news_links_mirrorspectator_com
from scraper.sites.bloomberght_com import get_news_links_bloomberght_com
from scraper.sites.nordicmonitor_com import get_news_links_nordicmonitor_com
from scraper.sites.sondakika_com import get_news_links_sondakika_com
from scraper.sites.tvpirveli_ge import get_news_links_tvpirveli_ge  
from scraper.sites.rustavi2_ge import get_news_links_rustavi2_ge
from scraper.sites.onetv import get_news_links_1tv_ge
from scraper.sites.mamul_am import get_news_links_mamul_am  
from scraper.sites.radiofarda_com import get_news_links_radiofarda_com
from scraper.sites.news_am import get_news_links_news_am
from scraper.sites.onein_am import get_news_links_1in_am    
from scraper.sites.uk_news_yahoo_com import get_news_links_uk_yahoo_com 
from scraper.sites.telegraph_co_uk import get_news_links_telegraph_co_uk
from scraper.sites.thesun_co_uk import get_news_links_thesun_co_uk
from scraper.sites.mirror_co_uk import get_news_links_mirror_co_uk
from scraper.sites.metro_co_uk import get_news_links_metro_co_uk
from scraper.sites.dailyrecord_co_uk import get_news_links_dailyrecord_co_uk  
from scraper.sites.express_co_uk import get_news_links_express_co_uk
from scraper.sites.manchestereveningnews_co_uk import get_news_links_manchestereveningnews_co_uk  
from scraper.sites.standart_co_uk import get_news_links_standard_co_uk
from scraper.sites.walesonline_co_uk import get_news_links_walesonline_co_uk
from scraper.sites.thescottishsun_co_uk import get_news_links_thescottishsun_co_uk
from scraper.sites.heraldscotland_com import get_news_links_heraldscotland_com
from scraper.sites.expressandstar_com import get_news_links_expressandstar_com
from scraper.sites.news_stv_tv import get_news_links_news_stv_tv
from scraper.sites.dailystar_co_uk import get_news_links_dailystar_co_uk
from scraper.sites.armenews_com import get_news_links_armenews_com
from scraper.sites.caucasefrance_com import get_news_links_caucasefrance_com
from scraper.sites.miasinnews_by import get_news_links_miasinnews_by
from scraper.sites.timesofindia_com import get_news_links_timesofindia_com  
from scraper.sites.ndtv_com import get_news_links_ndtv_com
from scraper.sites.walla_co_il import get_news_links_walla_co_il
from scraper.sites.ynet_co_il import get_news_links_ynet_co_il
from scraper.sites.mako_co_il import get_news_links_mako_co_il
from scraper.sites.tv13_co_li import get_news_links_13tv_co_il
from scraper.sites.israelhayom_com import get_news_links_israelhayom_com
from scraper.sites.timesofisrael_com import get_news_links_timesofisrael_com
from scraper.sites.jpost_com import get_news_links_jpost_com
from scraper.sites.newsru_co_il import get_news_links_newsru_co_il
from scraper.sites.cursorinfo_co_il import get_news_links_cursorinfo_co_il
from scraper.sites.tv9_co_il import get_news_links_9tv_co_il
from scraper.sites.israelinfo_co_il import get_news_links_israelinfo_co_il
from scraper.sites.mignews_com import get_news_links_mignews_com
from scraper.sites.alaraby_co_uk import get_news_links_alaraby_co_uk
from scraper.sites.alkhaleej_ae import get_news_links_alkhaleej_ae
from scraper.sites.aljazeera_net import get_news_links_aljazeera_net
from scraper.sites.aawsat_com import get_news_links_aawsat_com
from scraper.sites.alkhaleejonline_net import get_news_links_alkhaleejonline_net
from scraper.sites.arabi21_com import get_news_links_arabi21_com
from scraper.sites.arab48_com import get_news_links_arab48_com
from scraper.sites.okaz_com_sa import get_news_links_okaz_com_sa
from scraper.sites.spa_gov_sa import get_news_links_spa_gov_sa
from scraper.sites.qna_org_qa import get_news_links_qna_org_qa  
from scraper.sites.wam_ae import get_news_links_wam_ae
from scraper.sites.alsumaria_tv import get_news_links_alsumaria_tv
from scraper.sites.omannews_gov_om import get_news_links_omannews_gov_om
from scraper.sites.kuna_net_kw import get_news_links_kuna_net_kw
from scraper.sites.bna_bh import get_news_links_bna_bh
from scraper.sites.nna_leb_gov_lb import get_news_links_nna_leb_gov_lb
from scraper.sites.sana_sy import get_news_links_sana_sy    
from scraper.sites.alittihad_tv import get_news_links_alittihad_tv
from scraper.sites.syriahr_com import get_news_links_syriahr_com    
from scraper.sites.southfront_press import get_news_links_southfront_press
from scraper.sites.ina_iq import get_news_links_ina_iq
from scraper.sites.dc_fes_de import get_news_links_dc_fes_de
from scraper.sites.freiheit_org import get_news_links_freiheit_org
from scraper.sites.boell_de import get_news_links_boell_de
from scraper.sites.hss_de import get_news_links_hss_de
from scraper.sites.speigel_de import get_news_links_spiegel_de
from scraper.sites.bild_de import get_news_links_bild_de    
from scraper.sites.zdfheute_de import get_news_links_zdfheute_de
from scraper.sites.rsf_org import get_news_links_rsf_org
from scraper.sites.almanar_com_lb import get_news_links_almanar_com_lb
from scraper.sites.iswnews_com import get_news_links_iswnews_com
from scraper.sites.longwarjournal_org import get_news_links_longwarjournal_org
from scraper.sites.pakobserver_net import get_news_links_pakobserver_net
from scraper.sites.afghanistan_ru import get_news_links_afghanistan_ru
from scraper.sites.voanews_com import get_news_links_voanews_com
from scraper.sites.makorrishon_co_il import get_news_links_makorrishon_co_il
from scraper.sites.vesti_ru import get_news_links_vesti_ru
from scraper.sites.kp_ru import get_news_links_kp_ru
from scraper.sites.mikroskopmedia_com import get_news_links_mikroskopmedia_com
from scraper.sites.amnesty_org import get_news_links_amnesty_org
from scraper.sites.rambler_ru import get_news_links_rambler_ru
from scraper.sites.gazeta_ru import get_news_links_gazeta_ru
from scraper.sites.rg_ru import get_news_links_rg_ru
from scraper.sites.aif_ru import get_news_links_aif_ru
from scraper.sites.interfax_ru import get_news_links_interfax_ru      
from scraper.sites.ntv_ru import get_news_links_ntv_ru  
from scraper.sites.news_mail_ru import get_news_links_news_mail_ru 
from scraper.sites.rediff_com import get_news_links_rediff_com 
from scraper.sites.moneycontrol_com import get_news_links_moneycontrol_com
from scraper.sites.economictimes_indiatimes_com import get_news_links_economictimes_indiatimes_com
from scraper.sites.onmanorama_com import get_news_links_onmanorama_com
from scraper.sites.mathrubhumi_com import get_news_links_mathrubhumi_com
from scraper.sites.dw_com_en import get_news_links_dw_com
from scraper.sites.ir_voanews_com import get_news_links_ir_voanews_com
from scraper.sites.asrirsan_com import get_news_links_asriran_com
from scraper.sites.rajanews_com import get_news_links_rajanews_com
from scraper.sites.jahannews_com import get_news_links_jahannews_com
from scraper.sites.beytoote_com import get_news_links_beytoote_com
from scraper.sites.tehrantimes_com import get_news_links_tehrantimes_com
from scraper.sites.iranpress_com import get_news_links_iranpress_com
from scraper.sites.sharghdaily_com import get_news_links_shargdaily_com
from scraper.sites.nournews_ir import get_news_links_nournews_ir
from scraper.sites.mizanonline_ir import get_news_links_mizanonline_ir
from scraper.sites.inn_ir import get_news_links_inn_ir
from scraper.sites.irannewsupdate_com import get_news_links_irannewsupdate_com
from scraper.sites.ettelaat_com import get_news_links_ettelaat_com
from scraper.sites.bahardaily_ir import get_news_links_bahardaily_ir
from scraper.sites.resalat_news_com import get_news_links_resalat_news_com
from scraper.sites.icana_ir import get_news_links_icana_ir
from scraper.sites.siasatrooz_ir import get_news_links_siasatrooz_ir
from scraper.sites.mardomsalari_ir import get_news_links_mardomsalari_ir
from scraper.sites.vatanemrooz_ir import get_news_links_vatanemrooz_ir
from scraper.sites.esfahanemrooz_ir import get_news_links_esfahanemrooz_ir
from scraper.sites.iran_emrooz_net import get_news_links_iran_emrooz_net
from scraper.sites.jahanesanat_ir import get_news_links_jahanesanat_ir
from scraper.sites.eghtesademeli_com import get_news_links_eghtesademeli_com
from scraper.sites.eghtesadepooya_ir import get_news_links_eghtesadepooya_ir    
from scraper.sites.toseeirani_ir import get_news_links_toseeirani_ir
from scraper.sites.sayeh_news_com import get_news_links_sayeh_news_com
from scraper.sites.hamdelidaily_com import get_news_links_hamdelidaily_ir
from scraper.sites.iranpressnews_com import get_news_links_iranpressnews_com
from scraper.sites.theiranpost_com import get_news_links_theiranpost_com
from scraper.sites.dailysabah_com import get_news_links_dailysabah_com
from scraper.sites.wanaen_com import get_news_links_wanaen_com
from scraper.sites.mek_iran_com import get_news_links_mek_iran_com
from scraper.sites.mojahedin_org import get_news_links_mojahedin_org
from scraper.sites.nejatngo_org import get_news_links_nejatngo_org
from scraper.sites.imna_ir import get_news_links_imna_ir
from scraper.sites.iranfocus_com import get_news_links_iranfocus_com
from scraper.sites.themoscowtimes_com import get_news_links_themoscowtimes_com
from scraper.sites.meduza_io import get_news_links_meduza_io
from scraper.sites.rt_com import get_news_links_rt_com
from scraper.sites.kyivpost_com import get_news_links_kyivpost_com

from scraper.celery_task.find_problem import generate_problems
from scraper.celery_task.notify import notify_unsent_problems
from tasks.send_keyword_match_notify import build_temp_mail_data,send_digest_emails,build_temp_telegram_data,send_digest_telegrams


@shared_task
def celery_send_keywords_emails():
    send_digest_emails()
    
@shared_task
def celery_build_temp_mail_data():
    build_temp_mail_data()
    



@shared_task
def celery_send_keywords_telegram():
    send_digest_telegrams()
    
    
@shared_task
def celery_build_temp_telegram_data():
    build_temp_telegram_data()
    



@shared_task
def celery_check_fields():
    generate_problems()

@shared_task
def celery_notify():
    notify_unsent_problems()


import asyncio
import threading
from scraper.telegram.telegram_client import get_telegram_client
from utils.process_article import process_article_data_telegram
from telethon.tl.types import MessageMediaPhoto
from scraper.models import Source
from utils.photo_save import telegram_buffer_to_django_file,build_telegram_image_url

from telethon.tl.types import MessageMediaPhoto
from io import BytesIO



async def scrape_channel(channel_url, source_name, limit=10):
    client = get_telegram_client()
    await client.connect()

    if not await client.is_user_authorized():
        print("Session is not authorized.")
        return

    entity = await client.get_entity(channel_url)

    async for msg in client.iter_messages(entity, limit=limit):
        title = (msg.text[:80] + "...") if msg.text and len(msg.text) > 80 else msg.text
        content = msg.text
        link = f"{channel_url}/{msg.id}"
        news_shared_date = msg.date

        gallery_images = []

        if msg.media and isinstance(msg.media, MessageMediaPhoto):
            buffer = BytesIO()
            await client.download_media(msg, file=buffer)
            django_file = telegram_buffer_to_django_file(buffer, msg.media.photo.id)
            image_url = build_telegram_image_url(channel_url, msg.id, msg.media.photo)
            gallery_images.append({
                "image_url": image_url,
                "django_file": django_file
            })

        if msg.grouped_id:
            async for grouped_msg in client.iter_messages(entity, limit=10):
                if grouped_msg.grouped_id == msg.grouped_id and grouped_msg.id != msg.id:
                    if grouped_msg.media and isinstance(grouped_msg.media, MessageMediaPhoto):
                        buffer = BytesIO()
                        await client.download_media(grouped_msg, file=buffer)
                        django_file = telegram_buffer_to_django_file(buffer, grouped_msg.media.photo.id)
                        image_url = build_telegram_image_url(channel_url, grouped_msg.id, grouped_msg.media.photo)
                        gallery_images.append({
                            "image_url": image_url,
                            "django_file": django_file
                        })

        threading.Thread(
            target=process_article_data_telegram,
            kwargs=dict(
                source_name=source_name,
                link=link,
                title=title,
                content=content,
                gallery_images=gallery_images,
                news_shared_date=news_shared_date
            )
        ).start()

    await client.disconnect()





@shared_task(name="scraper.tasks.scrape_bbc_channel")
def scrape_bbc_channel():
    source = Source.objects.filter(link="https://t.me/BBCWorldoffl").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_oxuaze_channel")
def scrape_oxuaze_channel():
    source = Source.objects.filter(link="https://t.me/oxuaze").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))



@shared_task(name="scraper.tasks.scrape_reartsakh_channel")
def scrape_reartsakh_channel():
    source = Source.objects.filter(link="https://t.me/reartsakh").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))
    
    
@shared_task(name="scraper.tasks.scrape_bagramyan26_channel")
def scrape_bagramyan26_channel():
    source = Source.objects.filter(link="https://t.me/bagramyan26").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))
    
    
@shared_task(name="scraper.tasks.scrape_economy_of_armenia_channel")
def scrape_economy_of_armenia_channel():
    source = Source.objects.filter(link="https://t.me/economyofarmenia").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_miacum_channel")
def scrape_miacum_channel():
    source = Source.objects.filter(link="https://t.me/miacum").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))
    
    
@shared_task(name="scraper.tasks.scrape_mika_badalyan_channel")
def scrape_mika_badalyan_channel():
    source = Source.objects.filter(link="https://t.me/mikayelbad").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))
    
    
@shared_task(name="scraper.tasks.scrape_sismasis_channel")
def scrape_sismasis_channel():
    source = Source.objects.filter(link="https://t.me/sisumasis").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_karabakh_records_channel")
def scrape_karabakh_records_channel():
    source = Source.objects.filter(link="https://t.me/KarabakhRecords").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))
    
    
@shared_task(name="scraper.tasks.scrape_russkaya_obsina_zov_channel")
def scrape_russkaya_obsina_zov_channel():
    source = Source.objects.filter(link="https://t.me/obshina_ru").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))




@shared_task(name="scraper.tasks.scrape_meydan_tv_channel")
def scrape_meydan_tv_channel():
    source = Source.objects.filter(link="https://t.me/meydantv").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_azadliq_radiosu_channel")
def scrape_azadliq_radiosu_channel():
    source = Source.objects.filter(link="https://t.me/azadliqkanali").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_eco_expert_channel")
def scrape_eco_expert_channel():
    source = Source.objects.filter(link="https://t.me/eco_expert").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_qafqaz_info_channel")
def scrape_qafqaz_info_channel():
    source = Source.objects.filter(link="https://t.me/qafqazinfo").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_modern_azz_channel")
def scrape_modern_azz_channel():
    source = Source.objects.filter(link="https://t.me/modern_azz").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_baku_es_channel")
def scrape_baku_es_channel():
    source = Source.objects.filter(link="https://t.me/baku_es").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_shedevr_plus_channel")
def scrape_shedevr_plus_channel():
    source = Source.objects.filter(link="https://t.me/shedevrplus").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_isayevios_channel")
def scrape_isayevios_channel():
    source = Source.objects.filter(link="https://t.me/isayevios").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_azxeber1_channel")
def scrape_azxeber1_channel():
    source = Source.objects.filter(link="https://t.me/azxeber1").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_maraqli_tv_channel")
def scrape_maraqli_tv_channel():
    source = Source.objects.filter(link="https://t.me/maraqli_tv").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_bakutvxeber_channel")
def scrape_bakutvxeber_channel():
    source = Source.objects.filter(link="https://t.me/bakutvxeber").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_Axaraz_channel")
def scrape_Axaraz_channel():
    source = Source.objects.filter(link="https://t.me/Axaraz").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_tvictimai_channel")
def scrape_tvictimai_channel():
    source = Source.objects.filter(link="https://t.me/tvictimai").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_operativmedia_channel")
def scrape_operativmedia_channel():
    source = Source.objects.filter(link="https://t.me/operativmedia").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_sonxeberler_channel")
def scrape_sonxeberler_channel():
    source = Source.objects.filter(link="https://t.me/sonxeberler").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_P_apirus_channel")
def scrape_P_apirus_channel():
    source = Source.objects.filter(link="https://t.me/P_apirus").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_trthaberdijital_channel")
def scrape_trthaberdijital_channel():
    source = Source.objects.filter(link="https://t.me/trthaberdijital").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_gundemedairhs_channel")
def scrape_gundemedairhs_channel():
    source = Source.objects.filter(link="https://t.me/gundemedairhs").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_bpthaber_channel")
def scrape_bpthaber_channel():
    source = Source.objects.filter(link="https://t.me/bpthaber").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_konseyhaber_channel")
def scrape_konseyhaber_channel():
    source = Source.objects.filter(link="https://t.me/konseyhaber").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_turkiyedenhaberler24_channel")
def scrape_turkiyedenhaberler24_channel():
    source = Source.objects.filter(link="https://t.me/turkiyedenhaberler24").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_PulseGundem_channel")
def scrape_PulseGundem_channel():
    source = Source.objects.filter(link="https://t.me/PulseGundem").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_ataturkcumedyaorg_channel")
def scrape_ataturkcumedyaorg_channel():
    source = Source.objects.filter(link="https://t.me/ataturkcumedyaorg").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))
    
    
    
    
    
    
@shared_task(name="scraper.tasks.scrape_rian_ru_channel")
def scrape_rian_ru_channel():
    source = Source.objects.filter(link="https://t.me/rian_ru").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_nwsru_channel")
def scrape_nwsru_channel():
    source = Source.objects.filter(link="https://t.me/nwsru").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_anna_news_channel")
def scrape_anna_news_channel():
    source = Source.objects.filter(link="https://t.me/anna_news").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_bbcrussian_channel")
def scrape_bbcrussian_channel():
    source = Source.objects.filter(link="https://t.me/bbcrussian").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_lentadnya_channel")
def scrape_lentadnya_channel():
    source = Source.objects.filter(link="https://t.me/lentadnya").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_uniannet_channel")
def scrape_uniannet_channel():
    source = Source.objects.filter(link="https://t.me/uniannet").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_breakingmash_channel")
def scrape_breakingmash_channel():
    source = Source.objects.filter(link="https://t.me/breakingmash").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_bbbreaking_channel")
def scrape_bbbreaking_channel():
    source = Source.objects.filter(link="https://t.me/bbbreaking").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_moscowach_channel")
def scrape_moscowach_channel():
    source = Source.objects.filter(link="https://t.me/moscowach").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_bazabazon_channel")
def scrape_bazabazon_channel():
    source = Source.objects.filter(link="https://t.me/bazabazon").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_readovkanews_channel")
def scrape_readovkanews_channel():
    source = Source.objects.filter(link="https://t.me/readovkanews").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_rt_russian_channel")
def scrape_rt_russian_channel():
    source = Source.objects.filter(link="https://t.me/rt_russian").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_rbc_news_channel")
def scrape_rbc_news_channel():
    source = Source.objects.filter(link="https://t.me/rbc_news").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_tass_agency_channel")
def scrape_tass_agency_channel():
    source = Source.objects.filter(link="https://t.me/tass_agency").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_infomoscow24_channel")
def scrape_infomoscow24_channel():
    source = Source.objects.filter(link="https://t.me/infomoscow24").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_tvrain_channel")
def scrape_tvrain_channel():
    source = Source.objects.filter(link="https://t.me/tvrain").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))


@shared_task(name="scraper.tasks.scrape_e1_news_channel")
def scrape_e1_news_channel():
    source = Source.objects.filter(link="https://t.me/e1_news").first()
    source_name = source.name
    if not source:
        return
    asyncio.run(scrape_channel(source.link, source_name))




@shared_task()
def fetch_news_links_oxu():
    get_news_links_oxu(request=None)
    

@shared_task()
def fetch_news_links_apa():
    get_news_links_apa(request=None)
    
    
@shared_task()
def fetch_news_links_report():
    get_news_links_report(request=None)
    
    
# @shared_task()
# def fetch_news_links_azertag():
#     get_news_links_azertag(request=None)
    
    
@shared_task()
def fetch_news_links_editor():
    get_news_links_editor(request=None)
    
    
@shared_task()
def fetch_news_links_azxeber():
    get_news_links_azxeber(request=None)
    
    
@shared_task()
def fetch_news_links_lent():
    get_news_links_lent(request=None)
    
    
@shared_task()
def fetch_news_links_metbuat():
    get_news_links_metbuat(request=None)
    
    
# @shared_task()
# def fetch_news_links_bakuws():
#     get_news_links_bakuws(request=None)
    
    
@shared_task()
def fetch_news_links_xezerxeber():
    get_news_links_xezerxeber(request=None)
    
    
    
    
@shared_task()
def fetch_news_links_trend():
    get_news_links_trend(request=None)


@shared_task()
def fetch_news_links_milli():
    get_news_links_milli(request=None)
    
# #-------------FOREIGN NEWS----------------
    
    
    
# @shared_task()
# def fetch_news_links_bbc():
#     get_news_links_bbc(request=None)
    
    
@shared_task()
def fetch_news_links_armeniatoday():
    get_news_links_armeniatoday(request=None)


# @shared_task()
# def fetch_news_links_sputnikarm():
#     get_news_links_sputnikarm(request=None)




@shared_task()
def fetch_news_links_lentaru():
    get_news_links_lentaru(request=None)


@shared_task()
def fetch_news_links_izru():
    get_news_links_izru(request=None)


# # @shared_task()
# # def fetch_news_links_kpru():
# #     get_news_links_kpru(request=None)
    

# @shared_task()
# def fetch_news_links_civilge():
#     get_news_links_civilge(request=None)




# @shared_task()
# def fetch_news_links_trthaber():
#     get_news_links_trthaber(request=None)


# @shared_task()
# def fetch_news_links_internethaber():
#     get_news_links_internethaber(request=None)
    
    
@shared_task()
def fetch_news_links_infoxru():
    get_news_links_infoxru(request=None)
    
    
    
# @shared_task()
# def fetch_news_links_mirror():
#     get_news_links_mirror(request=None)
    
    
@shared_task()
def fetch_news_links_sozcu():
    get_news_links_sozcu(request=None)
    
    
@shared_task()
def fetch_news_links_cumhuriyet():
    get_news_links_cumhuriyet(request=None)
    
    
@shared_task()
def fetch_news_links_samanyoluhaber():
    get_news_links_samanyoluhaber(request=None)
    


# @shared_task()
# def fetch_news_links_haberturk():
#     get_news_links_haberturk(request=None)

@shared_task()
def fetch_news_links_sabah():
    get_news_links_sabah(request=None)
    
    
    
@shared_task()
def fetch_news_links_gercekgundem():
    get_news_links_gercekgundem(request=None)
    
    

@shared_task()
def fetch_news_links_agos():
    get_news_links_agos(request=None)

@shared_task()
def fetch_news_links_birgun():
    get_news_links_birgun(request=None)
    
    
@shared_task()
def fetch_news_links_bianet():
    get_news_links_bianet(request=None)



@shared_task()
def fetch_news_links_voaturkce():
    get_news_links_voaturkce(request=None)
    
    
    
    
@shared_task()
def fetch_news_links_anlatilaninotesi():
    get_news_links_anlatilaninotesi(request=None)
    
    
@shared_task()
def fetch_news_links_dwcom():
    get_news_links_dwcom(request=None)


@shared_task()
def fetch_news_links_ulusal():
    get_news_links_ulusal(request=None)

@shared_task()
def fetch_news_links_haberler():
    get_news_links_haberler(request=None)


@shared_task()
def fetch_news_links_rasthaber():
    get_news_links_rasthaber(request=None)
    
    
@shared_task()
def fetch_news_links_yeniakit():
    get_news_links_yeniakit(request=None)


@shared_task()
def fetch_news_links_yenisafak():
    get_news_links_yenisafak(request=None)
    
    
@shared_task()
def fetch_news_links_milliyet():
    get_news_links_milliyet(request=None)
    
    
@shared_task()
def fetch_news_links_hdp():
    get_news_links_hdp(request=None)


@shared_task()
def fetch_news_links_aa():
    get_news_links_aa(request=None)



@shared_task()
def fetch_news_links_kronos38():
    get_news_links_kronos38(request=None)
    
    
@shared_task()
def fetch_news_links_unian_net():
    get_news_links_unian_net(request=None)
    
    
    
@shared_task()
def fetch_news_links_belta_by():
    get_news_links_belta_by(request=None)
    
    
@shared_task()
def fetch_news_links_rbc_ua():
    get_news_links_rbc_ua(request=None)
    
    
@shared_task()
def fetch_news_links_tass_ru():
    get_news_links_tass_ru(request=None)
    
    
    
@shared_task()
def fetch_news_links_nv_ua():
    get_news_links_nv_ua(request=None)
    
    
@shared_task()
def fetch_news_links_az_sputniknews_ru():
    get_news_links_az_sputniknews_ru(request=None)
    
    
    
@shared_task()
def fetch_news_links_centralasia_media():
    get_news_links_centralasia_media(request=None)
    
    
@shared_task()
def fetch_news_links_gazeta_uz():
    get_news_links_gazeta_uz(request=None)
    
    
@shared_task()
def fetch_news_links_nur_kz():
    get_news_links_nur_kz(request=None)


@shared_task()
def fetch_news_links_orda_kz():
    get_news_links_orda_kz(request=None)
    
    
@shared_task()
def fetch_news_links_kaztag_kz():
    get_news_links_kaztag_kz(request=None)
    
    
@shared_task()
def fetch_news_links_uz_sputniknews_ru():
    get_news_links_uz_sputniknews_ru(request=None)
    
    
@shared_task()
def fetch_news_links_am_sputniknews_ru():
    get_news_links_am_sputniknews_ru(request=None)
    
    
@shared_task()
def fetch_news_links_sputnik_georgia_ru():
    get_news_links_sputnik_georgia_ru(request=None)
    
    
@shared_task()
def fetch_news_links_norharatch_com():
    get_news_links_norharatch_com(request=None)
    
    
@shared_task()
def fetch_news_links_newsgeorgia_ge():
    get_news_links_newsgeorgia_ge(request=None)
    
    
@shared_task()
def fetch_news_links_mtavari_tv():
    get_news_links_mtavari_tv(request=None)
    
    
    
@shared_task()
def fetch_news_links_formulanews_ge():
    get_news_links_formulanews_ge(request=None)
    
    
@shared_task()
def fetch_news_links_arm_sputniknews_ru():
    get_news_links_arm_sputniknews_ru(request=None)
    
    
@shared_task()
def fetch_news_links_yerevan_today():
    get_news_links_yerevan_today(request=None)
    
    
    
@shared_task()
def fetch_news_links_newsarmenia_am():
    get_news_links_newsarmenia_am(request=None)
    
    
    
@shared_task()
def fetch_news_links_aravot_am():
    get_news_links_aravot_am(request=None)
    
    
    
@shared_task()
def fetch_news_links_infoport_am():
    get_news_links_infoport_am(request=None)
    
    
@shared_task()
def fetch_news_links_armenpress_am():
    get_news_links_armenpress_am(request=None)
    
    
@shared_task()
def fetch_news_links_arminfo_info():
    get_news_links_arminfo_info(request=None)
    
@shared_task()
def fetch_news_links_armenianweekly_com():
    get_news_links_armenianweekly_com(request=None)
    

@shared_task()
def fetch_news_links_irna_ir():
    get_news_links_irna_ir(request=None)
    
    
@shared_task()
def fetch_news_links_alef_ir():
    get_news_links_alef_ir(request=None)
    
    
@shared_task()
def fetch_news_links_etemadonline_com():
    get_news_links_etemadonline_com(request=None)
    
    
    
@shared_task()
def fetch_news_links_esnafnews_com():
    get_news_links_esnafnews_com(request=None)
    
    
@shared_task()
def fetch_news_links_donya_e_eqtesad_com():
    get_news_links_donya_e_eqtesad_com(request=None)


@shared_task()
def fetch_news_links_entekhab_ir():
    get_news_links_entekhab_ir(request=None)
    
    
@shared_task()
def fetch_news_links_irdiplomacy_ir():
    get_news_links_irdiplomacy_ir(request=None)


@shared_task()
def fetch_news_links_kayhan_london():
    get_news_links_kayhan_london(request=None)

@shared_task()
def fetch_news_links_sedayemardom_net():
    get_news_links_sedayemardom_net(request=None)


@shared_task()
def fetch_news_links_zeitoons_com():
    get_news_links_zeitoons_com(request=None)


@shared_task()
def fetch_news_links_fararu_com():
    get_news_links_fararu_com(request=None)


@shared_task()
def fetch_news_links_ilna_ir():
    get_news_links_ilna_ir(request=None)
    
    
@shared_task()
def fetch_news_links_hamshahrionline_ir():
    get_news_links_hamshahrionline_ir(request=None)
    
@shared_task()
def fetch_news_links_khabaronline_ir():
    get_news_links_khabaronline_ir(request=None)



@shared_task()
def fetch_news_links_mehrnews_com():
    get_news_links_mehrnews_com(request=None)


@shared_task()
def fetch_news_links_mashreghnews_ir():
    get_news_links_mashreghnews_ir(request=None)


@shared_task()
def fetch_news_links_aftabnews_ir():
    get_news_links_aftabnews_ir(request=None)
    
    
    
@shared_task()
def fetch_news_links_tejaratnews_com():
    get_news_links_tejaratnews_com(request=None)


@shared_task()
def fetch_news_links_mojnews_com():
    get_news_links_mojnews_com(request=None)


@shared_task()
def fetch_news_links_atna_atu_ac_ir():
    get_news_links_atna_atu_ac_ir(request=None)
    
    
@shared_task()
def fetch_news_links_melliun_org():
    get_news_links_melliun_org(request=None)


@shared_task()
def fetch_news_links_isna_ir():
    get_news_links_isna_ir(request=None)
    
    
@shared_task()
def fetch_news_links_npr_org():
    get_news_links_npr_org(request=None)
    
    
@shared_task()
def fetch_news_links_calmatters_org():
    get_news_links_calmatters_org(request=None)
    
    
    
@shared_task()
def fetch_news_links_foxnews_com():
    get_news_links_foxnews_com(request=None)
    
    
@shared_task()
def fetch_news_links_huffpost_com():
    get_news_links_huffpost_com(request=None)
    
    
@shared_task()
def fetch_news_links_kqed_org():
    get_news_links_kqed_org(request=None)
    
    
@shared_task()
def fetch_news_links_pbs_org():
    get_news_links_pbs_org(request=None)
    
    
    
@shared_task()
def fetch_news_links_nbcnews_com():
    get_news_links_nbcnews_com(request=None)
    
    
@shared_task()
def fetch_news_links_news_sky_com():
    get_news_links_skynews_com(request=None)
    
    
@shared_task()
def fetch_news_links_theguardian_com():
    get_news_links_theguardian_com(request=None)


@shared_task()
def fetch_news_links_theconversation_com():
    get_news_links_theconversation_com(request=None)
    
    
@shared_task()
def fetch_news_links_vox_com():
    get_news_links_vox_com(request=None)

@shared_task()
def fetch_news_links_independent_co_uk():
    get_news_links_independent_co_uk(request=None)
    
    
@shared_task()
def fetch_news_links_msnbc_com():
    get_news_links_msnbc_com(request=None)
    
    
@shared_task()
def fetch_news_links_newsweek_com():
    get_news_links_newsweek_com(request=None)
    


@shared_task()
def fetch_news_links_thehindu_com():
    get_news_links_thehindu_com(request=None)
    
    
@shared_task()
def fetch_news_links_yahoo_com():
    get_news_links_yahoo_com(request=None)


@shared_task()
def fetch_news_links_boston_com():
    get_news_links_boston_com(request=None)


@shared_task()
def fetch_news_links_greatreporter_com():
    get_news_links_greatreporter_com(request=None)
    
    
@shared_task()
def fetch_news_links_cbsnews_com():
    get_news_links_cbsnews_com(request=None)
    
    
@shared_task()
def fetch_news_links_ipsnews_net():
    get_news_links_ipsnews_net(request=None)


@shared_task()
def fetch_news_links_upi_com():
    get_news_links_upi_com(request=None)


@shared_task()
def fetch_news_links_sbs_com_au():
    get_news_links_sbs_com_au(request=None)
    
    
@shared_task()
def fetch_news_links_latimes_com():
    get_news_links_latimes_com(request=None)


@shared_task()
def fetch_news_links_thedispatch_com():
    get_news_links_thedispatch_com(request=None)



@shared_task()
def fetch_news_links_globalnews_ca():
    get_news_links_globalnews_ca(request=None)


@shared_task()
def fetch_news_links_chp_org_tr():
    get_news_links_chp_org_tr(request=None)
    
    
@shared_task()
def fetch_news_links_nydailynews_com():
    get_news_links_nydailynews_com(request=None)


@shared_task()
def fetch_news_links_iyiparti_org_tr():
    get_news_links_iyiparti_org_tr(request=None)


@shared_task()
def fetch_news_links_tr_euronews_com():
    get_news_links_tr_euronews_com(request=None)


@shared_task()
def fetch_news_links_24news_ge():
    get_news_links_24news_ge(request=None)


@shared_task()
def fetch_news_links_interpressnews_ge():
    get_news_links_interpressnews_ge(request=None)
    

@shared_task()
def fetch_news_links_aysor_am():
    get_news_links_aysor_am(request=None)


@shared_task()
def fetch_news_links_tert_am():
    get_news_links_tert_am(request=None)
    
    
@shared_task()
def fetch_news_links_qomnews_ir():
    get_news_links_qomnews_ir(request=None) 


@shared_task()
def fetch_news_links_iribnews_ir():
    get_news_links_iribnews_ir(request=None)
    
    
@shared_task()
def fetch_news_links_news_gooya_ir():
    get_news_links_goyanews_com(request=None)


@shared_task()
def fetch_news_links_tasnimnews_com():
    get_news_links_tasnimnews_com(request=None)
    
    
@shared_task()
def fetch_news_links_tabnak_ir():
    get_news_links_tabnak_ir(request=None)
    
    
    
@shared_task()
def fetch_news_links_qafqazagency_ir():
    get_news_links_qafqazagency_ir(request=None)
    
    
@shared_task()
def fetch_news_links_gunaz_tv():
    get_news_links_gunaz_tv(request=None)
    
    
@shared_task()
def fetch_news_links_gadtb_com():
    get_news_links_gadtb_com(request=None)
    
    
@shared_task()
def fetch_news_links_hoosk_ir():
    get_news_links_hoosk_ir(request=None)
    
    
@shared_task()
def fetch_news_links_tehranprelacy_com():
    get_news_links_tehranprelacy_com(request=None)
    
    
@shared_task()
def fetch_news_links_rokna_net():
    get_news_links_rokna_net(request=None)
    
    
@shared_task()
def fetch_news_links_jamejamonline_ir():
    get_news_links_jamejamonline_ir(request=None)
    
    
@shared_task()
def fetch_news_links_fardanews_com():
    get_news_links_fardanews_com(request=None)
    
    
@shared_task()
def fetch_news_links_dailymail_co_uk():
    get_news_links_dailymail_co_uk(request=None)
    
    
@shared_task()
def fetch_news_links_bbc_com():
    get_news_links_bbc_com(request=None)
    
    
@shared_task()
def fetch_news_links_slate_com():
    get_news_links_slate_com(request=None)
    
    

@shared_task()
def fetch_news_links_nypost_com():
    get_news_links_nypost_com(request=None)
    
    
@shared_task()
def fetch_news_links_chicagotribune_com():
    get_news_links_chicagotribune_com(request=None)
    
    
@shared_task()
def fetch_news_links_radiozamaneh_com():
    get_news_links_radiozamaneh_com(request=None)
    
    
@shared_task()
def fetch_news_links_bbcpersian_com():  
    get_news_links_bbcpersian_com(request=None)


@shared_task()
def fetch_news_links_farsnews_ir():    
    get_news_links_farsnews_ir(request=None)
    
    
@shared_task()
def fetch_news_links_rfi_fr_fa():
    get_news_links_rfi_fr_fa(request=None)
    
    
@shared_task()
def fetch_news_links_iranwire_com():
    get_news_links_iranwire_com_en(request=None)
    
    
@shared_task()
def fetch_news_links_avatoday_net():
    get_news_links_avatoday_net(request=None)
    
    
@shared_task()
def fetch_news_links_balatarin_com():
    get_news_links_balatarin_com(request=None)
    

@shared_task()
def fetch_news_links_english_alarabiya_net():
    get_news_links_english_alarabiya_net(request=None)



@shared_task()
def fetch_news_links_iranintl_com():
    get_news_links_iranintl_com(request=None)
    
    
@shared_task()
def fetch_news_links_mirrorspectator_com():
    get_news_links_mirrorspectator_com(request=None)
    
    
@shared_task()
def fetch_news_links_bloomberght_com():
    get_news_links_bloomberght_com(request=None)
    
    
@shared_task()
def fetch_news_links_nordicmonitor_com():
    get_news_links_nordicmonitor_com(request=None)
    
    
@shared_task()
def fetch_news_links_sondakika_com():
    get_news_links_sondakika_com(request=None)
    
    
@shared_task()
def fetch_news_links_tvpirveli_ge():
    get_news_links_tvpirveli_ge(request=None)
    
    
@shared_task()
def fetch_news_links_rustavi2_ge():
    get_news_links_rustavi2_ge(request=None)
    
    
@shared_task()
def fetch_news_links_onetv_ge():
    get_news_links_1tv_ge(request=None)
    
    
@shared_task()
def fetch_news_links_mamul_am():
    get_news_links_mamul_am(request=None)
    
    
@shared_task()
def fetch_news_links_radiofarda_com():
    get_news_links_radiofarda_com(request=None)
    
    
@shared_task()
def fetch_news_links_news_am():
    get_news_links_news_am(request=None)
    
    
@shared_task()
def fetch_news_links_onein_am():
    get_news_links_1in_am(request=None)
    
    
@shared_task()
def fetch_news_links_uk_yahoo_com():
    get_news_links_uk_yahoo_com(request=None)
    

@shared_task()
def fetch_news_links_telegraph_co_uk():
    get_news_links_telegraph_co_uk(request=None)
    
    
@shared_task()
def fetch_news_links_thesun_co_uk():
    get_news_links_thesun_co_uk(request=None)
    
    
@shared_task()
def fetch_news_links_mirror_co_uk():
    get_news_links_mirror_co_uk(request=None)
    
    
@shared_task()
def fetch_news_links_metro_co_uk():
    get_news_links_metro_co_uk(request=None)
    
    
@shared_task()
def fetch_news_links_dailyrecord_co_uk():       
    get_news_links_dailyrecord_co_uk(request=None)
    
    
@shared_task()
def fetch_news_links_express_co_uk():
    get_news_links_express_co_uk(request=None)
    
    
@shared_task()
def fetch_news_links_manchestereveningnews_co_uk():
    get_news_links_manchestereveningnews_co_uk(request=None)
    
    
@shared_task()
def fetch_news_links_standard_co_uk():
    get_news_links_standard_co_uk(request=None)
    
    
@shared_task()
def fetch_news_links_walesonline_co_uk():
    get_news_links_walesonline_co_uk(request=None)
    
    
@shared_task()
def fetch_news_links_thescottishsun_co_uk():
    get_news_links_thescottishsun_co_uk(request=None)
    
    
@shared_task()
def fetch_news_links_heraldscotland_com():      
    get_news_links_heraldscotland_com(request=None)
    
    
@shared_task()
def fetch_news_links_expressandstar_com():
    get_news_links_expressandstar_com(request=None)


@shared_task()
def fetch_news_links_news_stv_tv():
    get_news_links_news_stv_tv(request=None)
    
    
@shared_task()
def fetch_news_links_dailystar_co_uk():
    get_news_links_dailystar_co_uk(request=None)
    
    
@shared_task()
def fetch_news_links_armenews_com():
    get_news_links_armenews_com(request=None)
    
    
@shared_task()
def fetch_news_links_caucasefrance_com():
    get_news_links_caucasefrance_com(request=None)
    
    
@shared_task()
def fetch_news_links_miasinnews_by():
    get_news_links_miasinnews_by(request=None)
    
    

@shared_task()
def fetch_news_links_timesofindia_com():
    get_news_links_timesofindia_com(request=None)
    
    
@shared_task()
def fetch_news_links_ndtv_com():
    get_news_links_ndtv_com(request=None)
    
    
@shared_task()
def fetch_news_links_walla_co_il():     
    get_news_links_walla_co_il(request=None)
    
    
@shared_task()
def fetch_news_links_ynet_co_il():
    get_news_links_ynet_co_il(request=None)
    
    
@shared_task()
def fetch_news_links_mako_co_il():
    get_news_links_mako_co_il(request=None)
    
    
@shared_task()
def fetch_news_links_13tv_co_il():
    get_news_links_13tv_co_il(request=None)
    
    
@shared_task()
def fetch_news_links_israelhayom_com():
    get_news_links_israelhayom_com(request=None)
    
    
    
@shared_task()
def fetch_news_links_timesofisrael_com():
    get_news_links_timesofisrael_com(request=None)
    
    
@shared_task()
def fetch_news_links_jpost_com():
    get_news_links_jpost_com(request=None)
    
    
@shared_task()
def fetch_news_links_newsru_co_il():
    get_news_links_newsru_co_il(request=None)
    
    
@shared_task()
def fetch_news_links_cursorinfo_co_il():
    get_news_links_cursorinfo_co_il(request=None)
    
    
@shared_task()
def fetch_news_links_9tv_co_il():
    get_news_links_9tv_co_il(request=None)
    
    
@shared_task()
def fetch_news_links_israelinfo_co_il():
    get_news_links_israelinfo_co_il(request=None)
    
    
@shared_task()
def fetch_news_links_mignews_com():
    get_news_links_mignews_com(request=None)


@shared_task()
def fetch_news_links_alaraby_co_uk():
    get_news_links_alaraby_co_uk(request=None)
    
    
@shared_task()
def fetch_news_links_alkhaleej_ae():
    get_news_links_alkhaleej_ae(request=None)
    
    
@shared_task()
def fetch_news_links_aljazeera_net():   
    get_news_links_aljazeera_net(request=None)
    
    
@shared_task()
def fetch_news_links_aawsat_com():
    get_news_links_aawsat_com(request=None)
    
    
@shared_task()
def fetch_news_links_alkhaleejonline_net():
    get_news_links_alkhaleejonline_net(request=None)
    
    
@shared_task()
def fetch_news_links_arabi21_com():
    get_news_links_arabi21_com(request=None)
    
    
    
@shared_task()
def fetch_news_links_arab48_com():
    get_news_links_arab48_com(request=None)
    
    
    
@shared_task()
def fetch_news_links_okaz_com_sa():
    get_news_links_okaz_com_sa(request=None)
    
    
    
@shared_task()
def fetch_news_links_spa_gov_sa():
    get_news_links_spa_gov_sa(request=None)
    
    
@shared_task()
def fetch_news_links_qna_org_qa():
    get_news_links_qna_org_qa(request=None)
    
    
@shared_task()
def fetch_news_links_wam_ae():
    get_news_links_wam_ae(request=None)
    
    
@shared_task()
def fetch_news_links_alsumaria_tv():
    get_news_links_alsumaria_tv(request=None)
    
    
    
@shared_task()
def fetch_news_links_omannews_gov_om():
    get_news_links_omannews_gov_om(request=None)
    
    
@shared_task()
def fetch_news_links_kuna_net_kw():
    get_news_links_kuna_net_kw(request=None)
    
    
    
@shared_task()
def fetch_news_links_bna_bh():
    get_news_links_bna_bh(request=None)
    
    
@shared_task()
def fetch_news_links_nna_leb_gov_lb():
    get_news_links_nna_leb_gov_lb(request=None)
    
    
@shared_task()
def fetch_news_links_sana_sy():
    get_news_links_sana_sy(request=None)
    
    
@shared_task()
def fetch_news_links_alittihad_tv():
    get_news_links_alittihad_tv(request=None)
    
    
    
@shared_task()
def fetch_news_links_syriahr_com():
    get_news_links_syriahr_com(request=None)
    
    
@shared_task()
def fetch_news_links_southfront_press():
    get_news_links_southfront_press(request=None)
    
    
@shared_task()
def fetch_news_links_ina_iq():
    get_news_links_ina_iq(request=None)
    
    

@shared_task()
def fetch_news_links_dc_fes_de():
    get_news_links_dc_fes_de(request=None)
    
    
@shared_task()
def fetch_news_links_freiheit_org():
    get_news_links_freiheit_org(request=None)
    
    
@shared_task()
def fetch_news_links_boell_de():
    get_news_links_boell_de(request=None)
    
    
@shared_task()
def fetch_news_links_hss_de():
    get_news_links_hss_de(request=None)
    
    
@shared_task()
def fetch_news_links_spiegel_de():
    get_news_links_spiegel_de(request=None)


@shared_task()
def fetch_news_links_bild_de():
    get_news_links_bild_de(request=None)
    
    
    
@shared_task()
def fetch_news_links_zdfheute_de():
    get_news_links_zdfheute_de(request=None)
    
    
    
@shared_task()
def fetch_news_links_rsf_org():
    get_news_links_rsf_org(request=None)
    
    
    
@shared_task()
def fetch_news_links_almanar_com_lb():
    get_news_links_almanar_com_lb(request=None)
    
    
@shared_task()
def fetch_news_links_iswnews_com():
    get_news_links_iswnews_com(request=None)



@shared_task()
def fetch_news_links_longwarjournal_org():
    get_news_links_longwarjournal_org(request=None)
    
    
@shared_task()
def fetch_news_links_pakobserver_net():
    get_news_links_pakobserver_net(request=None)


@shared_task()
def fetch_news_links_afghanistan_ru():
    get_news_links_afghanistan_ru(request=None)
    
    
@shared_task()
def fetch_news_links_voanews_com():
    get_news_links_voanews_com(request=None)


@shared_task()
def fetch_news_links_makorrishon_co_il():
    get_news_links_makorrishon_co_il(request=None)
    
    
@shared_task()
def fetch_news_links_vesti_ru():
    get_news_links_vesti_ru(request=None)
    
    
@shared_task()
def fetch_news_links_kp_ru():
    get_news_links_kp_ru(request=None)
    
    
@shared_task()
def fetch_news_links_mikroskopmedia_com():
    get_news_links_mikroskopmedia_com(request=None)
    
    
@shared_task()
def fetch_news_links_amnesty_org():
    get_news_links_amnesty_org(request=None) 
    
    
@shared_task()
def fetch_news_links_rambler_ru():
    get_news_links_rambler_ru(request=None)    
    
    
@shared_task()
def fetch_news_links_gazeta_ru():
    get_news_links_gazeta_ru(request=None)
    
    
@shared_task()
def fetch_news_links_rg_ru():
    get_news_links_rg_ru(request=None)
    
    
@shared_task()
def fetch_news_links_aif_ru():
    get_news_links_aif_ru(request=None)
    

@shared_task()
def fetch_news_links_interfax_ru():
    get_news_links_interfax_ru(request=None)
    
    
@shared_task()
def fetch_news_links_ntv_ru():
    get_news_links_ntv_ru(request=None)
    
    
@shared_task()
def fetch_news_links_news_mail_ru():
    get_news_links_news_mail_ru(request=None)
    
    
@shared_task()
def fetch_news_links_rediff_com():
    get_news_links_rediff_com(request=None)
    
    
@shared_task()
def fetch_news_links_moneycontrol_com():
    get_news_links_moneycontrol_com(request=None)
    
    
@shared_task()
def fetch_news_links_economictimes_indiatimes_com():
    get_news_links_economictimes_indiatimes_com(request=None)
    
    
    
@shared_task()
def fetch_news_links_onmanorama_com():
    get_news_links_onmanorama_com(request=None)
    
    
@shared_task()
def fetch_news_links_mathrubhumi_com():
    get_news_links_mathrubhumi_com(request=None)
    
    
@shared_task()
def fetch_news_links_dw_com_en():
    get_news_links_dw_com(request=None)
    
@shared_task()
def fetch_news_links_ir_voanews_com():
    get_news_links_ir_voanews_com(request=None)
    
    
    
@shared_task()
def fetch_news_links_asriran_com():
    get_news_links_asriran_com(request=None)

@shared_task()
def fetch_news_links_rajanews_com():
    get_news_links_rajanews_com(request=None)
    
    
    
@shared_task()
def fetch_news_links_jahannews_com():
    get_news_links_jahannews_com(request=None)
    
    
@shared_task()
def fetch_news_links_beytoote_com():
    get_news_links_beytoote_com(request=None)   
    
@shared_task()
def fetch_news_links_tehrantimes_com():
    get_news_links_tehrantimes_com(request=None)
    
    
@shared_task()
def fetch_news_links_iranpress_com():
    get_news_links_iranpress_com(request=None)
    
    
    
@shared_task()
def fetch_news_links_sharghdaily_com():
    get_news_links_shargdaily_com(request=None)
    
    
@shared_task()
def fetch_news_links_nournews_ir():
    get_news_links_nournews_ir(request=None)
    
    
@shared_task()
def fetch_news_links_mizanonline_ir():
    get_news_links_mizanonline_ir(request=None)
    
    
@shared_task()
def fetch_news_links_inn_ir():
    get_news_links_inn_ir(request=None)
    
    
@shared_task()
def fetch_news_links_irannewsupdate_com():
    get_news_links_irannewsupdate_com(request=None)
    
    
@shared_task()
def fetch_news_links_ettelaat_com():
    get_news_links_ettelaat_com(request=None)    


@shared_task()
def fetch_news_links_bahardaily_ir():
    get_news_links_bahardaily_ir(request=None)
    
    
@shared_task()
def fetch_news_links_resalat_news_com():
    get_news_links_resalat_news_com(request=None)
    
    
@shared_task()
def fetch_news_links_icana_ir():
    get_news_links_icana_ir(request=None)   
    
    

@shared_task()
def fetch_news_links_siasatrooz_ir():
    get_news_links_siasatrooz_ir(request=None)
    
    
@shared_task()
def fetch_news_links_mardomsalari_ir():
    get_news_links_mardomsalari_ir(request=None)
    
    
@shared_task()
def fetch_news_links_vatanemrooz_ir():
    get_news_links_vatanemrooz_ir(request=None)
    
    
@shared_task()
def fetch_news_links_esfahanemrooz_ir():
    get_news_links_esfahanemrooz_ir(request=None)
    
    
    
@shared_task()
def fetch_news_links_iran_emrooz_net():
    get_news_links_iran_emrooz_net(request=None)
    
    
@shared_task()
def fetch_news_links_jahanesanat_ir():
    get_news_links_jahanesanat_ir(request=None)
    
    
@shared_task()
def fetch_news_links_eghtesademeli_com():
    get_news_links_eghtesademeli_com(request=None)
    
    

@shared_task()
def fetch_news_links_eghtesadepooya_ir():
    get_news_links_eghtesadepooya_ir(request=None)
    
    
    
@shared_task()
def fetch_news_links_toseeirani_ir():
    get_news_links_toseeirani_ir(request=None)
    
    
@shared_task()
def fetch_news_links_sayeh_news_com():
    get_news_links_sayeh_news_com(request=None)
    
    
@shared_task()
def fetch_news_links_hamdelidaily_ir():
    get_news_links_hamdelidaily_ir(request=None)
    
    
    
@shared_task()
def fetch_news_links_iranpressnews_com():
    get_news_links_iranpressnews_com(request=None)
    
    
@shared_task()
def fetch_news_links_theiranpost_com():
    get_news_links_theiranpost_com(request=None)



@shared_task()
def fetch_news_links_dailysabah_com():
    get_news_links_dailysabah_com(request=None)
    
    
@shared_task()
def fetch_news_links_wanaen_com():
    get_news_links_wanaen_com(request=None)
    
    
    
@shared_task()
def fetch_news_links_mek_iran_com():
    get_news_links_mek_iran_com(request=None)
    
    
    
@shared_task()
def fetch_news_links_mojahedin_org():
    get_news_links_mojahedin_org(request=None)
    
    
@shared_task()
def fetch_news_links_nejatngo_org():
    get_news_links_nejatngo_org(request=None)
    
    
@shared_task()
def fetch_news_links_imna_ir():
    get_news_links_imna_ir(request=None)
    
    
    
@shared_task()
def fetch_news_links_iranfocus_com():
    get_news_links_iranfocus_com(request=None)


@shared_task()
def fetch_news_links_themoscowtimes_com():
    get_news_links_themoscowtimes_com(request=None)
    
    
@shared_task()
def fetch_news_links_meduza_io():
    get_news_links_meduza_io(request=None)
    
    
@shared_task()
def fetch_news_links_rt_com():
    get_news_links_rt_com(request=None)
    
    
@shared_task()
def fetch_news_links_kyivpost_com():
    get_news_links_kyivpost_com(request=None)
