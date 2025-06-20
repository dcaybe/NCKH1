# Generated by Django 5.1.6 on 2025-06-05 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_nckh9', '0004_rules'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analysts',
            name='allStudent',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='analysts',
            name='good',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='analysts',
            name='needImprove',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='analysts2',
            name='allStudent',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='analysts2',
            name='good',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='analysts2',
            name='needImprove',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='asyncexporttask',
            name='progress',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='asyncsynctask',
            name='failed_records',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='asyncsynctask',
            name='processed_records',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='asyncsynctask',
            name='progress',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='asyncsynctask',
            name='total_records',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='gvcndanhgia',
            name='diemCDSV',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='gvcndanhgia',
            name='diemNCKH',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='gvcndanhgia',
            name='drl_tongket',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='gvcndanhgia',
            name='khoaHoc',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='gvcndanhgia',
            name='kqHocTap',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='gvcndanhgia',
            name='maSV',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='gvcndanhgia',
            name='thanhtichHoatDong',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='gvcndanhgia',
            name='thanhvienBCS',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='historypoint',
            name='hocky1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historypoint',
            name='hocky10',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historypoint',
            name='hocky11',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historypoint',
            name='hocky12',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historypoint',
            name='hocky13',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historypoint',
            name='hocky14',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historypoint',
            name='hocky15',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historypoint',
            name='hocky16',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historypoint',
            name='hocky17',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historypoint',
            name='hocky18',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historypoint',
            name='hocky19',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historypoint',
            name='hocky2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historypoint',
            name='hocky20',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historypoint',
            name='hocky3',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historypoint',
            name='hocky4',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historypoint',
            name='hocky5',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historypoint',
            name='hocky6',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historypoint',
            name='hocky7',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historypoint',
            name='hocky8',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historypoint',
            name='hocky9',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historypoint',
            name='maSV',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='hocky',
            name='hoc_ky',
            field=models.FloatField(choices=[(1, 'Học kỳ 1'), (2, 'Học kỳ 2')]),
        ),
        migrations.AlterField(
            model_name='hocky',
            name='nam_hoc',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='hoidongkhoachamdiem',
            name='diemCDSV',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='hoidongkhoachamdiem',
            name='diemNCKH',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='hoidongkhoachamdiem',
            name='drl_tongket',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='hoidongkhoachamdiem',
            name='khoaHoc',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='hoidongkhoachamdiem',
            name='kqHocTap',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='hoidongkhoachamdiem',
            name='maSV',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='hoidongkhoachamdiem',
            name='thanhtichHoatDong',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='hoidongkhoachamdiem',
            name='thanhvienBCS',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='homepagemanager',
            name='allStudent',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='homepagemanager',
            name='pending',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='infostudent',
            name='khoaHoc',
            field=models.FloatField(default=2023),
        ),
        migrations.AlterField(
            model_name='infostudent',
            name='maSV',
            field=models.FloatField(unique=True),
        ),
        migrations.AlterField(
            model_name='infostudent',
            name='phone',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='infostudent',
            name='phoneCoVan',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='infoteacher',
            name='maGV',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='infoteacher',
            name='phone',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='login',
            name='maSV',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='lophoc',
            name='khoa_hoc',
            field=models.FloatField(verbose_name='Khóa học'),
        ),
        migrations.AlterField(
            model_name='nofiticationmanager',
            name='allNotification',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='pendingstudents',
            name='drl_tongket',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='pendingstudents',
            name='maSV',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='ranking',
            name='maSV',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='ranking',
            name='rank_number',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='rules',
            name='max_points',
            field=models.FloatField(default=0, verbose_name='Điểm tối đa'),
        ),
        migrations.AlterField(
            model_name='rules',
            name='order',
            field=models.FloatField(default=0, verbose_name='Thứ tự hiển thị'),
        ),
        migrations.AlterField(
            model_name='sinhvientdg',
            name='diemCDSV',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='sinhvientdg',
            name='diemNCKH',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='sinhvientdg',
            name='drl_tongket',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='sinhvientdg',
            name='khoaHoc',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='sinhvientdg',
            name='kqHocTap',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='sinhvientdg',
            name='maSV',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='sinhvientdg',
            name='thanhtichHoatDong',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='sinhvientdg',
            name='thanhvienBCS',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='teachermanager',
            name='allClass',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='teachermanager',
            name='allStudent',
            field=models.FloatField(),
        ),
    ]
